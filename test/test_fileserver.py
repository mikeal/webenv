import httplib2
import os 
import functest

from webenv.applications.file_server import FileServerApplication
from webenv import FileResponse

this_directory = os.path.abspath(os.path.dirname(__file__))

def setup_module(module):
    test_app = functest.registry['test_app']
    test_app.add_resource('files', FileServerApplication(os.path.join(this_directory, 'files')))

def test_png():
    h = httplib2.Http()
    uri = 'http://localhost:8888/files/mikeal.png'
    response, content = h.request(uri, 'GET')
    assert content == open(os.path.join(this_directory, 'files', 'mikeal.png'), 'r').read()
    assert response['content-type'] == FileResponse.content_type_table['png']
    