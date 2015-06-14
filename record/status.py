#coding: utf-8
import model
import socket

import requests
try: requests.packages.urllib3.disable_warnings()
except AttributeError: pass

from dns import resolver
    
statusfile = "/srv/log/statusfile.txt"
streaming_servers = [{'streaming1': '45.55.128.88'}]

"""This seemed like a good idea at the time..."""
class Status(str):
    statusmap = {'green': 0, 'yellow': 1, 'red': 2}

    def __eq__(self, other):
        try:
            return self.statusmap[str(self)] == self.statusmap[str(other)]
        except KeyError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.statusmap[self] > self.statusmap[other]

    def __lt__(self, other):
        return self.statusmap[self] < self.statusmap[other]

    def __ge__(self, other):
        return self.statusmap[self] >= self.statusmap[other]

    def __le__(self, other):
        return self.statusmap[self] <= self.statusmap[other]
    
    def __int__(self):
        return self.statusmap[self]
    
    def __bool__(self):
        return self.statusmap[self] == 0

class StatusState(object):
    def __init__(self, status, description=[], systems={}, age=0):
        self.status = Status(status)
        if type(description) == str:
            description = [description]
        self.description = description
        self.systems = systems
        self.age = age

    @property
    def name(self):
        _name = self.__class__.__name__
        if _name.endswith("Errors"):
            return _name[:-6].lower()
        else:
            return _name.lower()
    
    @classmethod
    def check(cls):
        checks = [c.check() for c in cls.__subclasses__()]
        status = max(c.status for c in checks)
        desc = reduce(lambda x, y: x+y, [a.description for a in checks])
        systems = {c.name: c.status for c in checks}
        age = cls.get_status_age()
        return cls(status, desc, systems, age)

    # will fail on IOError, trust cron to deliver error
    @property
    def changed(self):
        with open(statusfile, 'r') as f:
            savedstatus = f.read().strip().split(":")[0][:]
            return savedstatus != self.status
        
    def save(self):
        self.age += 1
        with open(statusfile, 'w') as f:
            f.write(str(self.status) + ":" + str(self.age))

    @classmethod
    def get_status_age(cls):
        with open(statusfile, 'r') as f:
            contents = f.read()
            return int(contents.strip().split(":")[1])

            
class WWWErrors(StatusState):
    @classmethod
    def check(cls):
        try:
            # Also checks certificate
            j = requests.get("https://lokun.is/www-status", timeout=4.20).json()
            assert j['status'] == "ok"
        except (AssertionError, Exception) as ex:
            if type(ex) is AssertionError:
                return cls("red", 'www: /www-status != {"status": "ok"}')
            else:
                return cls("red", "www: " + str(ex))
        return cls("green")

            
class DNSErrors(StatusState):
    @classmethod
    def check(cls):
        for host in ["", "api.", "www.", "vpn.", "vpn.beta."]:
            try:
                fqdn = host + "lokun.is"
                socket.gethostbyname(fqdn)
            except socket.gaierror as ex:
                return cls("red", "dns " + fqdn + ": " + str(ex))
            return cls("green")

            
class StreamingErrors(StatusState):
    """Streaming servers are named streamingN.lokun.is. For every
    streaming server, there also exists a dns record
    streamingN-t.lokun.is, that resolves to the same IP address as
    streamingN.lokun.is.

    Then each streaming server has a record in /etc/hosts overriding
    streamingN-t.lokun.is to resolv to the IP address for
    www.lokun.is.

    When this test queries https://streamingN-t.lokun.is, the
    streaming server will proxy the request to www.lokun.is because of
    the /etc/hosts entry.

    It is favourable to edit /etc/hosts on the streaming server
    because then the test fails if /etc/hosts fails.

    The test then asserts a statement about the json, confirming that
    it originated from www.lokun.is.

    """
    @classmethod
    def check(cls):
        errors = []
        for proxy in streaming_servers:
            try:
                 json = requests.get("https://" + proxy + "-t.lokun.is/www-status",verify=False).json()
                 assert json['status'] == "ok"
            except (requests.RequestException, AssertionError) as e:
                errors.append(e.message)

        if len(errors) == 0:
            return cls("green")
        return cls("yellow" if len(errors) == 1 else "red", errors)

"""This shouldnt be testing dns0.lokun.is and dns1.lokun.is,
DNSErrors should be doing this. Need to control in what order
StatusState calls its inheriterees. 

class OverrideDNSError(StatusState):
    @classmethod
    def check(cls):

        try:
            ovrdns = [resolver.query(a, "A")[0].to_text() for a in ['dns0.lokun.is', 'dns1.lokun.is']]
        except resolver.NXDOMAIN:
            return cls("red")
        myresolver = resolver.Resolver()
        myresolver.nameservers = ovrdns
        print myresolver.nameservers

"""     
        
class NodeErrors(StatusState):
    @classmethod
    def check(cls):
        status = "green"
        down = model.NodeList.down()
        if down:
            status = "yellow" if len(down) == 1 else "red"
        errors = []
        for n in down:
            if not n.selfcheck:
                errors.append(n.name + ": selfcheck False")
            if n.heartbeat_age > 12*60:
                s = "{0}: heartbeat_age == {1:.0f} min"
                errors.append(s.format(n.name, n.heartbeat_age/60))
        return cls(status, errors)
        


if __name__ == "__main__":
    state = StatusState.check()
    print state.systems
    print state.status
    print "\n".join(state.description)
