:mod:`webenv` --- WSGI request, response and application abstractions.
======================================================================

.. module:: webenv
   :synopsis: A thin abstraction layer on top of wsgi providing request, response and application abstractions.
.. moduleauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>
.. sectionauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>

.. class:: Application()

   WSGI application abstraction baseclass. 
   
   .. method:: handler(request)
   
      Method must be implemented by subclass. 
      
      Takes a :class:`Request` instance and returns a :class:`Response` instance.
      
      Simplest usage::
      
         from webenv import Application
         
         class MyApplication(Application):
             def handler(self, request):
                 if request.path == '/':
                     return HtmlResponse(open('index.html', 'r').read())

.. class:: Request(environ, start_response)

   Request object. 
   
   Environ keys are accessible using dictionary style syntax::
      
      request['SERVER_PROTOCOL']
   
   .. attribute:: body
   
      :class:`Body` instance.
      
   .. attribute:: method
   
      HTTP request method::
      
         if request.method == "GET":
      
   .. attribute:: headers
   
      :class:`Headers` instance.
      
.. class:: Body(request)

   Request Body Object.
   
   :func:`str` must be called on request object to get a string::
   
      body = str(request.body)
      
.. class:: Headers(request)

   HTTP headers object. 
   
   Lookup headers using dictionary style syntax::
   
      request.headers["accept-encoding"]
      
   Note: make sure this is done caseless.
   
.. class:: Response([body])

   HTTP Response object
   
   .. attribute:: status
   
      HTTP status, must be full response string not an integer status code.
      
      Default is `"200 Ok"`
      
   .. attribute:: content_type
   
      HTTP content-type, default is `"text/plain"`. 
      
      A list of acceptable content-types is http://en.wikipedia.org/wiki/Internet_media_type
   
   .. attribute:: body
   
      HTTP response body. If value has an iterator the iterator will be used in the response 
      objects iterator.
      
   .. method:: add_header(name, value)
   
      Add a header to the HTTP response::
      
         response.add_header('Cache-Controler', 'no-cache')

.. class:: HtmlResponse(body)

   HTML HTTP Response object. Subclass of :class:`Response`.
   
   Subclass of :class:`Response` with content_type `"text/html"`.
   
   `body` should be a string of HTML.

.. class:: FileResponse(file)

   File wrapper for HTTP Responses. Subclass of :class:`Response`.
   
   If *file* is a :func:`str` or a :func:`unicode` object it is assumed to a path to a local 
   filename and will be resolved. Any other type is assumed to be a 
   `File-like object <http://docs.python.org/library/stdtypes.html#file-objects>`_.
   
   The content-type is guessed by looking at the extension at the end of the requestion uri.
   You can override this by setting the :attr:`Response.content_type`.

   .. attribute:: readsize
   
      Size of the read chunks for the response iterator. Default is `1024`.

   .. attribute:: size
   
      Optional attribute. If a filename is given to the constructor the file size will be 
      used, if not size will not be set and the `content-length` header will not be set.
   
   .. method:: guess_content_type(path)
   
      Guess the :attr:`Response.content_type` given a specific path.
      
.. class Response303::
   
   HTTP 303 Response object. Subclass of :class:`Response`.

.. class Response404::

   HTTP 404 Response object. Subclass of :class:`Response`.

.. class Response403::

   HTTP 403 Response object. Subclass of :class:`Response`.

.. class Response405::

   HTTP 405 Response object. Subclass of :class:`Response`.

.. class Response500::

   HTTP 500 Response object. Subclass of :class:`Response`.

.. class ResponseTraceback::

   HTTP 500 Response with a Python Traceback in the body. Subclass of :class:`Response`.

.. class ResponseHtmlTraceback::

   HTTP 500 Response with a Python Traceback formatted in html. Subclass of :class:`Response`.
   
   Requires pygments to be installed. TODO, finish this.

:mod:`webenv.rest` --- Resource based application abstractions.
----------------------------------------------------------------------

.. module:: webenv.rest
   :synopsis: Resource based application abstractions.
.. moduleauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>
.. sectionauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>

.. class:: RestApplication()

   REST Application.
   
   Intended to be subclassed with the author defining methods :meth:`GET`, :meth:`POST`, 
   :meth:`PUT` and/or other HTTP methods.
   
   .. method:: GET(request[, *rest_args])
   
      HTTP GET handler. Not implemented by baseclass, optionally implemented by subclass.
      
      *request* is an instance of :class:`Request`.
      
      The request path is broken up and sent to rest_args::
      
         class MyRestApplication(RestApplication):
             def GET(self, request, action, user, method=None):
                 print action, user, method
                 return Response()

      Creates an application that prints::

         >>> urllib2.urlopen("http://localhost/action1/testuser")
         action1 testuser None
         >>> urllib2.urlopen("http://localhost/a/testuser/another.txt")
         a testuser another.txt

   .. method:: PUT(request[, *rest_args])
   
      HTTP PUT handler. Not implemented by baseclass, optionally implemented by subclass.
   
      Usage identical to :meth:`GET`.
   
   .. method:: POST(request[, *rest_args])
   
      HTTP POST handler. Not implemented by baseclass, optionally implemented by subclass.
      
      Usage identical to :meth:`GET`.
         
   .. method:: add_namespace(name, rest_application)

      Add a REST application to a specific namespace.
   
      This method allows you to reuse :class:`RestApplication` subclasses::
      
         class PagesApplication(RestApplication):
             def GET(self, request, *args):
                 print "Pages::", args
                 return Response()
         
         class IndexApplication(RestApplication):
             def GET(self, request, *args):
                 print "Index::", args
                 return Response()

         index_application = IndexApplication()
         index_application.add_namespace("pages", PagesApplication())

      And now `index_application` will print::
      
         >>> urllib2.urlopen("http://localhost/blah")
         Index:: ('blah')
         >>> urllib2.urlopen("http://localhost/pages/aa/bb/cc")
         Pages:: ('aa', 'bb', 'bb') 
      
:mod:`webenv.applications` --- Prebuilt webenv applications.
----------------------------------------------------------------------

.. module:: webenv.applications
   :synopsis: Prebuilt webenv applications.
.. moduleauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>
.. sectionauthor:: Mikeal Rogers <mikeal.rogers@gmail.com>

.. class:: FileServerApplication(basepath)

   File serving application.
   
   *basepath* is an absolute path to the base directory to be served.
   
   Is a subclass of :class:`webenv.rest.RestApplication` so it can be added as a namespace::
   
      class MyApplication(RestApplication):
          def GET(self, request):
              return FileResponse("/var/static/index.html")
              
      application = MyApplication()
      application.add_namespace("css", FileServerApplication("/var/css"))
      application.add_namespace("images", FileServerApplication("/var/images"))
      
   





