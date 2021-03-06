#coding:utf8
'''
http://tools.cherrypy.org/wiki/WindowsService
'''
"""
The most basic (working) CherryPy 3.0 Windows service possible.
Requires Mark Hammond's pywin32 package.
"""

import cherrypy
import win32serviceutil
import win32service
import win32event

class HelloWorld:
    """ Sample request handler class. """

    def index(self):
        return "Hello world1!"
    index.exposed = True


class MyService(win32serviceutil.ServiceFramework):
    """NT Service."""
    
    _svc_name_ = "CherryPyService"
    _svc_display_name_ = "CherryPy Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # create an event that SvcDoRun can wait on and SvcStop
        # can set.
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        cherrypy.tree.mount(HelloWorld(), '/')
        
        # in practice, you will want to specify a value for
        # log.error_file below or in your config file.  If you
        # use a config file, be sure to use an absolute path to
        # it, as you can't be assured what path your service
        # will run in.
        cherrypy.config.update({
            'global':{
                'engine.autoreload.on': False,
                'log.screen': False,
                'engine.SIGHUP': None,
                'engine.SIGTERM': None
                }
            })
        # set blocking=False so that start() does not block
        cherrypy.server.quickstart()
        cherrypy.engine.start(blocking=False)
        # now, block until our event is set...
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        cherrypy.server.stop()
        win32event.SetEvent(self.stop_event)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)


