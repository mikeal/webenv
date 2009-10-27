from webenv import Request, Response, Response404, Response500
from urlparse import urlparse

class RestApplication(object):
    request_class = Request
    def __init__(self, exclude_script_info=True):
        self.rest_resources = {}
        self.exclude_script_info = exclude_script_info
    def __call__(self, environ, start_response):
        request = self.request_class(environ, start_response)
        
        if self.exclude_script_info:
            path = environ['PATH_INFO']
        else:
            path = environ['SCRIPT_NAME'] + environ['PATH_INFO']
        
        if len(path) is 0:
            path = '/'
        
        if path.startswith('/'):
            path = [p for p in path.split('/') if len(p) is not 0]
        elif environ['PATH_INFO'].startswith('http'):
            path = [p for p in urlparse(path).path.split('/') if len(p) is not 0]
        else:
            raise Exception('Cannot read PATH_INFO '+request.full_uri+str(request.environ))
        
        if len(path) is 0:
            response = self.handler(request)
            if response is None:    
                response = Response500(str(type(self))+".handler() did not return a response object")
            response.request = request
            response.start_response()
            return response
        else:
            response = self.rest_handler(request, *path)
            if response is None:
                response = Response500(str(type(self))+".rest_handler() did not return a response object")
            response.request = request
            response.start_response()
            return response
            
    def rest_handler(self, request, *path):
        if len(path) is 0:
            return self.handler(request)
        path = list(path)
        key = path.pop(0)
        if not self.rest_resources.has_key(key):
            return self.handler(request, *[key]+path)
        return self.rest_resources[key].rest_handler(request, *path)
            
    def handler(self, request, *path):
        if not hasattr(self, request.method):
            return Response404("No "+request.method+" resource for "+request.full_uri)
        return getattr(self, request.method)(request, *path)

    def add_resource(self, ns, rest_application):
        self.rest_resources[ns] = rest_application
        
def StaticApplication(RestResponse):
    def __call__(self, data):
        self.data = data
    def GET(self):
        return Response(self.data)