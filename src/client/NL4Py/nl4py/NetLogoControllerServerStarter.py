'''NL4Py, A NetLogo controller for Python
Copyright (C) 2018  Chathika Gunaratne

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError
from py4j.protocol import Py4JError
import subprocess
import threading
import os
import atexit
import sys
import logging
import time
import psutil
import math
##############################################################################
'''Responsible for starting and stopping the NetLogo Controller Server'''
class NetLogoControllerServerStarter:
    
    __gw = None# New gateway connection 
    ##server is in netlogo app folder
    
    
    def __init__(self):
        self.__gw = JavaGateway()
        print('Shutting down old server instance...')
        self.shutdownServer()
        #atexit.register(self.shutdownServer)
    '''Internal method to start JavaGateway server. Will be called by starServer on seperate thread'''
    def __runServer(self): 
        __server_name = "nl4py.server.NetLogoControllerServer"
        try:
            nl_path = os.environ['NETLOGO_APP']
        except KeyError:
            #looks like the NETLOGO_APP variable isn't set... 
            #Trying to use os dependent defaults
            print("NETLOGO_APP was not set, trying to find NetLogo .jar files")
            import platform
            if(platform.system() == "Windows"):
                nl_path = "C:/Program Files/NetLogo 6.0.2/app"
            if(platform.system() == "Darwin"):
                nl_path = "/Applications/NetLogo 6.0.2/Java"
            pass
        
        nl_path = os.path.join(os.path.abspath(nl_path),"*")
        os.pathsep
        server_path = "./server/*"
        classpath = nl_path + os.pathsep + server_path
        xmx = psutil.virtual_memory().available / 1024 / 1024 / 1024
        xms = "-Xms" + str(int(math.floor(xmx - 2))) + "G"
        xmx = "-Xmx" + str(int(math.floor(xmx))) + "G"
        subprocess.call(["java",xmx,"-XX:-UseGCOverheadLimit","-cp", classpath,__server_name])
        
    '''Starts JavaGateway server'''
    def startServer(self):
        #Fire up the NetLogo Controller server through python
        thread = threading.Thread(target=self.__runServer, args=())
        thread.start()
        time.sleep(3)
        
    '''Send shutdown signal to the JavaGateway server. No further communication is possible unless server is restarted'''
    def shutdownServer(self):
         if(self.__gw != None):    
            try:
                logging.disable(logging.CRITICAL)
                __bridge = self.__gw.entry_point
                __bridge.shutdownServer()
                self.__gw.close(keep_callback_server=False, close_callback_server_connections=True)
                self.__gw = None
            except Exception as e:
                pass