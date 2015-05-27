#!/usr/bin/python2.7

import model
from status import StatusState
from common.logger import Logger
from time import time
from commands import getoutput
import os.path
import sys

logger = Logger("monitor", mailfrom="lokun@sudo.is")
errors = []
vpndown = []
empty = []
status = "green"

rrdroot = "/srv/rrd"
rrddb = "monitor_db.rrd"

def rrdupdate(ts, usercount, bw):
    rrdupdate = "rrdtool update {0} --template bandwidth:usercount {1}:{2}:{3}"
    r = rrdupdate.format(os.path.join(rrdroot, rrddb), ts, bw, usercount) 
    if "-v" in sys.argv: print r
    rrd = getoutput(r)
    return rrd

def creategraphs():
    graph_sh = os.path.join(rrdroot, "graph.sh")
    graph = getoutput("/usr/bin/bash {0}".format(graph_sh))
    if "-v" in sys.argv: print graph_sh
    return graph

def main():
    state = StatusState.check()
    state.save()
    if state.changed:
        # a systems property would be really nice
        send_report(state, True)
    elif state.get_count() % 16 == 0:
        send_report(state, False)

    nodes = model.NodeList.alive()
    counts, bw = map(sum, zip(*[(a.usercount, a.throughput) for a in nodes]))
    s_bw = "{0:.2f}".format(bw / 1000000.)

    logger.log("Usercount: " + str(counts))
    logger.log("Bandwidth usage: {0} mb/s".format(s_bw))

    rrd = rrdupdate(time(), counts, s_bw)
    if rrd.startswith("ERROR"):
        logger.log("rrdtool update: " + rrd)
    graphs = creategraphs()
    if "ERROR" in graphs:
        logger.log("rrdtool graph: " + rrd)

def send_report(state, email_on_green=False):
        status = state.status.upper()
        faulty = [a for a in state.systems if state.systems[a] != "green"]
        if state.status  == "green":
            logger.email("GREEN", subject="GREEN Lokun")
        else:
            logger.email("\n".join(state.description),
                         subject="{0} Lokun: {1}".format(status, faulty))

if __name__ == "__main__":
    main()
