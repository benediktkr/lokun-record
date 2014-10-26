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
    if time() % 3600 == 0:
        counts = [a.usercount for a in model.NodeList.enabled()]
        logger.log("Usercount: " + sum(count))
    if state.status != "green":
        # a systems property would be really nice
        status = state.status.upper()
        faulty = [a for a in state.systems if state.systems[a] != "green"]
        logger.email("\n".join(state.description),
                     subject="{0} Lokun: {1}".format(status, faulty))

if __name__ == "__main__":
    main()
