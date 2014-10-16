import os
import servicemanager
import signal
import sys
import time

def log(message):
    if 'stdout' in sys.argv:
        print(message)
    else:
        servicemanager.LogInfoMsg(message)

class Server(object):
    def __init__(self):
        self.exitFlag = False
   

    def run(self):
        while not self.exitFlag:
            pass


    def shutdown(self):
        log('%s server shutting down.' % __name__)
        # Do any cleanup here.
        # Exit
        self.exitFlag = True