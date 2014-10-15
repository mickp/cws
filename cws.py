import configparser
import os
import servicemanager
import win32service  
import win32serviceutil  
import win32event  
import socket

CONFIG_NAME = WindowsService

class CockpitWindowsService(win32serviceutil.ServiceFramework):  
    # Windows services parameters.
    _svc_name_ = None
    _svc_display_name_ = None
    _svc_description_ = None


    def __init__(self, args):
        config = configparser.ConfigParser()
        config.read('cws.conf')
        name = config.get(CONFIG_NAME, 'name')
        _svc_name_ = 'cockpit_' + name
        _svc_display_name_ = 'Cockpit ' + name + ' service.'
        _svc_description_ = 'Serves cockpit ' + name + ' objects.'

        self.device_module = config.get(CONFIG_NAME, 'module')

        # Initialise service framework.
        win32serviceutil.ServiceFramework.__init__(self,args)  
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)


    def log(self, message, error=False):
        if error:
            logFunc = servicemanager.LogErrorMsg
        else:
            logFunc = servicemanager.LogInfoMsg
        logFunc("%s: %s" % (self._svc_name_, message))


    def SvcDoRun(self):
        self.log("Starting.")
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            # start the Pyro servers
            # importlib(device_module)
        except e:
            self.logFunc(e, error=True)
            self.SvcStop()
            # Exit with a non-zero error code so Windows will attempt to restart.
            os.exit(-1)
        self.log("Waiting for stop_event.")
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)


    def SvcStop(self):  
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)   
        self.log("Stopping.")
        self.helper.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


if __name__ == '__main__':  
    win32serviceutil.HandleCommandLine(PyroDaemonService)  