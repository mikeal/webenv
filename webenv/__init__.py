from urlparse import urlparse
import traceback
import cgi
import os, sys

def reconstruct_url(environ):
    # From WSGI spec, PEP 333
    from urllib import quote
    url = environ['wsgi.url_scheme']+'://'
    if environ.get('HTTP_HOST'): url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']
        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
               url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
               url += ':' + environ['SERVER_PORT']
    url += environ.get('SCRIPT_NAME','')
    url += environ.get('PATH_INFO','')
    # Fix ;arg=value in url
    if url.find('%3B') is not -1:
        url, arg = url.split('%3B', 1)
        url = ';'.join([url, arg.replace('%3D', '=')])
    # Stick query string back in
    if environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']
    # Stick it in environ for convenience     
    environ['reconstructed_url'] = url
    return url

class Body(object):
    def __init__(self, request):
        self.request = request
        self.environ = request.environ
        self._body_data = None
        if self.request.environ['CONTENT_TYPE'] == "application/x-www-form-urlencoded":
            self.form = cgi.parse_qs(str(self))
    def __str__(self):
        if self._body_data is None:
            if self.request.environ.get('CONTENT_LENGTH'):
                length = int(self.request.environ['CONTENT_LENGTH'])
                self._body_data = self.request.environ['wsgi.input'].read(length)
            else:
                self._body_data = ''
        return self._body_data
    __unicode__ = __str__
    def __len__(self):
        if self.request.environ.get('CONTENT_LENGTH'):
            return int(self.request.environ['CONTENT_LENGTH'])
        return len(str(self))
        
    def __getitem__(self, name):
        if not hasattr(self, 'form'):
            raise Exception("This was not an urlencoded form POST.")
        result = self.form[name]
        if type(result) is list and len(result) is 1:
            return result[0]
        else:
            return result

class Headers(object):
    def __init__(self, request):
        self.request = request
        self.environ = request.environ
        self._hdict = {}
        for k, v in self.environ.items():
            if k.startswith('HTTP_'):
                k = k.replace('HTTP_', '', 1).swapcase().replace('_', '-')
                if not self._hdict.has_key(k): self._hdict[k] = v
        self.__dict__ = self._hdict
    def __getitem__(self, key):
        return self._hdict[key]
    
    def __str__(self):
        return str(self.__dict__)
    
    def items(self):
        return self._hdict.items()

class Request(object):
    def __init__(self, environ, start_response):
        self.environ = environ; self._start_response = start_response
        self._body = None
        self._method = None
        self._headers = None
        self._full_uri = None
        self._start_response_run = False
    
    @property
    def full_uri(self):
        if self._full_uri is None:
            self._full_uri = reconstruct_url(self.environ)
        return self._full_uri
        
    def start_response(self, status, headers):
        if not self._start_response_run:
            result = self._start_response(status, headers)    
            self._start_response_run = True
            return result
    
    def __call__(self, *args, **kwargs):
        return self.start_response(*args, **kwargs)
    def __getitem__(self, key):
        return self.environ[key]
    
    @property
    def body(self):
        if self._body is None:
            self._body = Body(self)
        return self._body
        
    @property
    def method(self):
        if self._method is None:
            self._method = getattr(self.headers, 'x-http-method-override', self.environ['REQUEST_METHOD']).upper()
        return self._method
        
    @property
    def headers(self):
        if self._headers is None:
            self._headers = Headers(self)
        return self._headers

class Application(object):
    request_class = Request
    def __call__(self, environ, start_response):
        request = self.request_class(environ, start_response)
        response = self.handler(request)
        response.request = request
        return response
        
class Response(object):
    """WSGI Response Abstraction. Requires that the request object is set to it before being returned in a wsgi application."""
    
    content_type = 'text/plain'
    status = '200 OK'
    
    def __init__(self, body=''):
        self.body = body
        self.headers = []
        
    def __iter__(self):
        self.headers.append(('content-type', self.content_type,))
        self.request.start_response(self.status, self.headers)
        if not hasattr(self.body, "__iter__"):
            yield self.body
        else:
            for x in self.body:
                yield x
        
    def add_header(self, n, v):
        self.headers.append((n,v,))
        
class HtmlResponse(Response):
    content_type = 'text/html'
        
class FileResponse(Response):
    readsize = 1024
    size = None
    content_type = None
    
    content_type_table = {'js': 'application/x-javascript', 'html': 'text/html; charset=utf-8',
                          'fallback':'text/plain; charset=utf-8', 'ogg': 'application/ogg', 
                          'xhtml':'text/html; charset=utf-8', 'rm':'audio/vnd.rn-realaudio', 
                          'swf':'application/x-shockwave-flash', 
                          'mp3': 'audio/mpeg', 'wma':'audio/x-ms-wma', 
                          'ra':'audio/vnd.rn-realaudio', 'wav':'audio/x-wav', 
                          'gif':'image/gif', 'jpeg':'image/jpeg',
                          'jpg':'image/jpeg', 'png':'image/png', 
                          'tiff':'image/tiff', 'css':'text/css; charset=utf-8',
                          'mpeg':'video/mpeg', 'mp4':'video/mp4', 
                          'qt':'video/quicktime', 'mov':'video/quicktime',
                          'wmv':'video/x-ms-wmv', 'atom':'application/atom+xml; charset=utf-8',
                          'xslt':'application/xslt+xml', 'svg':'image/svg+xml', 
                          'mathml':'application/mathml+xml', 
                          'rss':'application/rss+xml; charset=utf-8',
                          'ics':'text/calendar; charset=utf-8 '}
    
    def __init__(self, f):
        if type(f) in [str, unicode]:
            self.size = os.path.getsize(f)
            if os.name == 'nt' or sys.platform == 'cygwin':
                f = open(f, 'rb')
            else:
                f = open(f, 'r')
        self.f = f        
        self.headers = []
        
    def __iter__(self):
        self.add_header('Cache-Controler', 'no-cache')
        self.add_header('Pragma', 'no-cache')
        if self.size is not None:
            self.add_header('Content-Length', str(self.size))
        if self.content_type is None:
            self.content_type = self.guess_content_type(self.request.full_uri)            
        self.add_header('content-type', self.content_type)
        self.request.start_response('200 Ok', self.headers)     
        output = '\n'
        while len(output) is not 0:
            output = self.f.read(self.readsize)
            yield output

    def guess_content_type(self, path):
        """Make a best guess at the content type"""
        extention_split = path .split('.')

        if self.content_type_table.has_key(extention_split[-1]):
            return self.content_type_table[extention_split[-1]]
        else:
            return self.content_type_table['fallback']

class Response303(Response):
    status = '303 See Other'
    def __init__(self, uri):
        self.headers = []
        self.add_header('location', uri)
        self.body = 'Redirecting to new resource at '+uri
            
class Response404(Response):
    status = '404 Not Found'

class Response201(Response):
    status = '201 Created'

ResponseNotFound = Response404
    
class Response403(Response):
    status = '403 Forbidden'
    
ResponseForbidden = Response403

class Response405(Response):
    status = '405 Method Not Allowed'

ResponseMethodNotAllowed = Response405

class Response500(Response):
    status = '500 Internal Server Error'

ResponseInternalServerError = Response500

class ResponseTraceback(Response500):
    html = False
    def __init__(self, e):
        self.e = e
        self.headers = []
    
    @property
    def body(self):
        if not self.html:
            tb = traceback.format_exception(*sys.exc_info())
            return ''.join(tb)
        else:
            pass
            
class ResponseHtmlTraceback(ResponseTraceback):
    html = True