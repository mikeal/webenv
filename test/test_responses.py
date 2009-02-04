import functest
import httplib2
from webenv.rest import RestApplication
import webenv

class ResponseTests(RestApplication):
    def GET(self, request, test_class, *args):
        return getattr(webenv, test_class)(*args)

def setup_module(module):    
    test_app = functest.registry['test_app']    
    test_app.add_resource('responses', ResponseTests())

def httpget(url):
    h = httplib2.Http()
    return h.request(url, 'GET')

class ErrorResponseTest(object):
    
    def __init__(self, code):
        self.code = code
        self.__name__ = 'test_'+str(code)
    def __call__(self):
        response, content = httpget('http://localhost:8888/responses/Response'+str(self.code))
        assert response.status == self.code
        response, content = httpget('http://localhost:8888/responses/Response'+str(self.code)+'/Cannot')
        assert response.status == self.code and content == 'Cannot'

test_403 = ErrorResponseTest(403)
test_404 = ErrorResponseTest(404)
test_405 = ErrorResponseTest(405)
test_500 = ErrorResponseTest(500)

