import ConfigParser as configparser
import imp
import os
import servicemanager
from signal import CTRL_BREAK_EVENT
import socket
import subprocess
import sys
import win32api
import win32event 
from win32process import DETACHED_PROCESS
import win32serviceutil  
import win32service  

CONFIG_NAME = 'WindowsService'

# We need the full path to this file in order to find
# config files in the same folder when invoked as a service.
PATH = os.path.dirname(os.path.abspath(__file__))


class CockpitWindowsService(win32serviceutil.ServiceFramework):  
    """ Serves cockpit devices via a Windows service.

    Creates a service based on information in the 'WindowsService'
    section of a configuration file. The config. file must specify
    the service 'name' and a 'module' to serve.
    The module is run as a script.  When the service is stopped, it
    will send CTRL_BREAK_EVENT to the script: the script should override
    default SIGBREAK handler to do whatever cleanup it needs before
    exiting.
    """

    # Windows services parameters are needed before an instance is 
    # created, so must be set here: read the config and est them.
    config = configparser.ConfigParser()
    config.read(PATH + '\cws.conf')
    name = config.get(CONFIG_NAME, 'name')
    # Make the short service name CamelCase.
    _svc_name_ = ('cockpit ' + name).title().replace(' ', '')
    _svc_display_name_ = 'Cockpit ' + name + ' service.'
    _svc_description_ = 'Serves cockpit ' + name + ' objects.'
    # This is the device module that will be served.
    device_module = config.get(CONFIG_NAME, 'module')
    # Optional args that the module will be invoked with.
    if config.has_option(CONFIG_NAME, 'args'):
        module_args = config.get(CONFIG_NAME, 'args')
    else:
        module_args = []


    def __init__(self, args):
        # The process in which the server module is executed.
        self.child = None

        # Initialise service framework.
        win32serviceutil.ServiceFramework.__init__(self,args)  
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)


    def log(self, message, error=False):
        if error:
            logFunc = servicemanager.LogErrorMsg
        else:
            logFunc = servicemanager.LogInfoMsg
        print message
        logFunc("%s: %s" % (self._svc_name_, message))


    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        # Popen argument list: python.exe, the absolute path to the module
        # file and any optional args.
        # python.exe is literal because sys.executable because returns
        # pythonservice.exe which won't run our script.
        cmd = ['python.exe',
               imp.find_module(self.device_module)[1],
              ] + self.module_args.split(' ')
        # Popen kwargs.
        kwargs = {}
        # Set the correct path.
        kwargs['cwd'] = PATH
        # Create a new process group so we can send CTRL_BREAK_EVENTs.
        #kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
        kwargs['creationflags'] = DETACHED_PROCESS
        try:
            # Launch the script as a child process.
            self.child = subprocess.Popen(cmd, **kwargs)
        except Exception as e:
            self.log(e.message, error=True)
            # Exit with non-zero error code so Windows will attempt to restart.
            sys.exit(-1)
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        self.log('Launched %s\nPID %s' % (' '.join(cmd), self.child.pid))
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)


    def SvcStop(self):  
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log("Stopping - terminitaing process %s." % self.child.pid)
        # Try to send CTRL_BREAK_EVENT to the child process.
        #self.child.send_signal(CTRL_BREAK_EVENT)
        os.kill(self.child.pid, CTRL_BREAK_EVENT)
        #except:
        #    # If the child process has already exited, os.kill will produce
        #    # WindowsError: [Error 5] Access is denied.
        #    pass
        # Wait for the child process to do any cleanup.
        self.child.wait()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':  
    win32serviceutil.HandleCommandLine(CockpitWindowsService)  