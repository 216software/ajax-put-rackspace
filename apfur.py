# vim: set expandtab ts=4 sw=4 syntax=python fileencoding=utf8:

import argparse
import logging
import uuid
import wsgiref.simple_server


import pyrax

log = logging.getLogger('apfur')

"""

1.  Create a container on rackspace cloudfiles.

2.  Use python to set metadata on that container to allow CORS.

3.  Write some python code to build a temp URL for the PUT method.

4.  Write HTML to build a simple input type=file widget.

5.  Write some javascript so that when a user picks a file with the file
    input tag, we use a `FileReader <https://developer.mozilla.org/en-US/docs/Web/API/FileReader>`
    to read the contents of the file into a buffer.

6.  Use some more javascript to do an ajax PUT to the temp URL created
    in step 3.

"""

def parse_args():

    ap = argparse.ArgumentParser()

    ap.add_argument('rackspace_username')
    ap.add_argument('rackspace_API_key')

    return ap.parse_args()


def create_container(rackspace_username, rackspace_API_key):

    pyrax.set_setting('identity_type',  'rackspace')

    pyrax.set_credentials(
        rackspace_username,
        rackspace_API_key,
        region="ORD")

    logging.info("Set settings and credentials on pyrax")

    # It is safe to run create_container even if the container already
    # exists.
    uploads_container = pyrax.cloudfiles.create_container('uploads')

    return uploads_container

def serve_upload_page_1(upload_url):

    class MyApp(object):

        def __init__(self, upload_url):
            self.upload_url = upload_url

        def render_upload_page(self):

            page = open('./upload-1.html').read()
            return page.format(self.upload_url)

        def __call__(self, environ, start_response):

            start_response('200 OK', [])
            return [self.render_upload_page()]

    app = MyApp(upload_url)
    s = wsgiref.simple_server.make_server('', 8765, app)

    logging.info("About to fire up the wsgi server...")
    s.serve_forever()

if __name__ == '__main__':

    args = parse_args()

    logging.basicConfig(level=logging.DEBUG)

    log.info('Configured logging.')

    uploads_container = create_container(
        args.rackspace_username,
        args.rackspace_API_key)

    # Tell this container to accept AJAX requests from
    # sprout.216software.com.
    uploads_container.set_metadata({
        'Access-Control-Allow-Origin': 'sprout.216software.com'})

    filename = str(uuid.uuid4())

    log.info("File will be stored with name {0}.".format(filename))

    upload_url = pyrax.cloudfiles.get_temp_url(
        uploads_container, filename, 60*60, method='PUT')

    log.debug('upload_url: {0}'.format(upload_url))

    serve_upload_page_1(upload_url)
