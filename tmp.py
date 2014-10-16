import imp, os, sys, subprocess
import ConfigParser as configparser
from signal import CTRL_BREAK_EVENT
import time

CONFIG_NAME = 'WindowsService'

PATH = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(PATH + '\cws.conf')
device_module = config.get(CONFIG_NAME, 'module')

python = sys.executable
script = imp.find_module(device_module)[1]

child_process = subprocess.Popen([python, script, 'stdout'], cwd=PATH, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
time.sleep(1)       
child_process.send_signal(CTRL_BREAK_EVENT)   
child_process.wait()