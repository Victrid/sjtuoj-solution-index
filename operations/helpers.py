import logging
import os
from time import sleep, time

from systemd.journal import JournalHandler

log = logging.getLogger('stdlog')
log.addHandler(JournalHandler())
log.setLevel(logging.DEBUG)


def create_temp_folder():
    if os.path.exists("./.tmp"):
        if not os.path.isdir("./.tmp"):
            log.error("SJTUOJ Update Service: .tmp exists and is not a dir. aborting.")
            exit(-1)
    else:
        os.makedirs("./.tmp")
    os.system("rm -rf ./.tmp/*")
    log.debug("SJTUOJ Update Service: temp folder created.")


class LessRequest:
    def __init__(self):
        self.last_request = time()

    def __call__(self):
        if time() - self.last_request < 2:
            sleep(2)
        self.last_request = time()
        return


less_request = LessRequest()
