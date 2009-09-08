import os
from webenv.rest import RestApplication
from webenv import Response404, ResponseForbidden, HtmlResponse, FileResponse, Response201

class FileServerApplication(RestApplication):
    write_enabled = False
    directory_listings_enabled = True
    
    def __init__(self, basepath):
        self.basepath = os.path.abspath(basepath)
        self.rest_resources = {}
        
    def get_directory_listing_html(self, filename):
        return 'html'
        
    def GET(self, request, *path):
        filename = os.path.join(self.basepath, *path)
        if os.path.isdir(filename):
            if self.directory_listings_enabled:
                return HtmlResponse(self.get_directory_listing_html(filename))
        elif os.path.isfile(filename):
            return FileResponse(filename)
        else:
            return Response404('File does not Exist '+filename)
            
    def PUT(self, request, filename):
        if not self.write_enabled:
            return ResponseForbidden('Writes are not enabled on this file serving resource.')
        else:
            try:
                f = open(os.path.join(self.path, serve_file), 'w')
            except Exception, e:
                return TracebackResponse(e)
            return Response201('created')

