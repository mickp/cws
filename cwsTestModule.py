import signal
import sys

def shutdown(sig, frame):
    print 'shutdown called.'
    sys.exit()

print '__name__ is %s.' % __name__

if __name__ == '__main__':
    print '%s is __main__.' % __name__
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGABRT, shutdown)
    while True:
        pass