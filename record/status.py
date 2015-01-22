#coding: utf-8
import model
import socket

from requests import get as httpget

statusfile = "/srv/log/statusfile.txt"

"""This seemed like a good idea at the time..."""
class Status(str):
    statusmap = {'green': 0, 'yellow': 1, 'red': 2}

    def __eq__(self, other):
        return self.statusmap[str(self)] == self.statusmap[str(other)]

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
    def __init__(self, status, description=[], systems={}):
        self.status = Status(status)
        if type(description) == str:
            description = [description]
        self.description = description
        self.systems = systems

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
        return cls(status, desc, systems)
        
    @property
    def changed(self):
        try:
            with open(statusfile, 'r') as f:
                return f.read().strip()
        except IOError:
            # Catching IOError so a filesystem error doesn't
            # silently disable the monitor
            return StatusState("green")

    def save(self):
        try:
            with open(statusfile, 'w') as f:
                f.write(status)
        except IOError:
            pass

class WWWErrors(StatusState):
    @classmethod
    def check(cls):
        try:
            # Also checks certificate
            j = httpget("https://lokun.is/www-status", timeout=4.20).json()
            assert j['status'] == "ok"
            return cls("green")
        except (AssertionError, Exception) as ex:
            if type(ex) is AssertionError:
                return cls("red", 'www: /www-status != {"status": "ok"}')
            return cls("red", "www: " + str(ex))

class DNSErrors(StatusState):
    @classmethod
    def check(cls):
        for host in ["", "api.", "www.", "vpn.", "vpn.beta."]:
            try:
                fqdn = host + "lokun.is"
                socket.gethostbyname(fqdn)
                return cls("green")
            except socket.gaierror as ex:
                return cls("red", "dns " + fqdn + ": " + str(ex))


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
