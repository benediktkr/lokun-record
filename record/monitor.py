import model
import smtplib
from email.mime.text import MIMEText
import socket
from status import StatusState
from common.logger import Logger
from time import time

logger = Logger("monitor", mailfrom="lokun@sudo.is")
errors = []
vpndown = []
empty = []
status = "green"

def main():
    state = StatusState.check()
    if state.changed:
        state.save()
        # a systems property would be really nice
        status = state.status.upper()
        faulty = [a for a in state.systems if state.systems[a] != "green"]
        logger.email("\n".join(state.description),
                     subject="{0} Lokun: {1}".format(status, faulty))
    if time() % 360 < 5:
        nodes = model.NodeList.alive()
        counts, bw = map(sum, zip(*[(a.usercount, a.throughput) for a in nodes]))
        
        logger.log("Usercount: " + str(counts))
        logger.log("Bandwidth usage: {0:.2f}  mb/s".format(bw / 1000000.))

if __name__ == "__main__":
    main()
