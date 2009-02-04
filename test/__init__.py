import os
import threading
import functest
from time import sleep

from cherrypy import wsgiserver
from webenv.rest import RestApplication

class TestApplication(RestApplication):
    pass

def setup_module(module):
    test_app = TestApplication()
    functest.registry['test_app'] = test_app
    
    httpd = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8888), 
                       test_app, server_name='test_server', numthreads=50)
    module.httpd = httpd; module.thread = threading.Thread(target=httpd.start)
    module.thread.start()
    sleep(.5)
    
def teardown_module(module):
    while module.thread.isAlive():
        module.httpd.stop()
    
