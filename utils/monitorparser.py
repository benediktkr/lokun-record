from datetime import datetime
from time import mktime
from commands import getoutput
from collections import defaultdict
import sys

def getdate(line):
    return line.split('\t')[0]

def gettimestamp(date):
    t = mktime(datetime.strptime(date, "%Y-%m-%d %H:%M:%S" ).timetuple())
    return int(t)

def rrdupdate(ts, usercount, bw):
    rrdupdate = "rrdtool update monitor_db.rrd --template bandwidth:usercount {0}:{1}:{2}"
    r = rrdupdate.format(ts, bw, usercount) 
    if "-v" in sys.argv: print r
    rrd = getoutput(r)
    if rrd.startswith("ERROR"):
        print rrd
    return rrd

def parseline(line):
    date, text = line.split('\t')
    ts = gettimestamp(date)
    return (ts, text)

if __name__ == "__main__":
    with open('monitor.log', 'r') as f:
        monitor = f.readlines()

    print "preprocessing"
    pre = list()
    for i in xrange(len(monitor)):
        line = monitor[i]
        nextline = monitor[i+1] if i+1 < len(monitor) else ""
            
        try:
            ts, msg = parseline(line)
            nextts, nextmsg = parseline(nextline)
        except ValueError:
            continue
            
        if msg.startswith("Usercount:"):
            usercount = int(msg.split(": ")[1])
            if nextmsg.startswith("Bandwidth usage: "):
                bw = float(nextmsg.split(": ")[1].split(" ")[0])
            else:
                bw = 0
            pre.append((ts, usercount, bw))

    print "done, count:", len(monitor)
    print "rrdtool..."
    sys.exit()
    for value in pre:
        rrdupdate(*value)
    print "done."
