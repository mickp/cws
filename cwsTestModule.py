import os
import servicemanager
import signal
import sys
import time

exitFlag = False

def log(message):
    if 'stdout' in sys.argv:
        print(message)
    else:
        servicemanager.LogInfoMsg(message)
    

def shutdown(sig, frame):
    log('Shutting down with signal %s' % sig)
    # Do any cleanup here.
    # Exit
    sys.exit()

if __name__ == '__main__':  
    msg = 'TestModule started in %s, PID %s' % (__name__, os.getpid())
    msg += '\nArgs were:\n'
    msg += ' '.join(sys.argv)
    log(msg)

    # Override SIGBREAK
    signal.signal(signal.SIGBREAK, shutdown)
    
    # Main loop
    while True:
        pass