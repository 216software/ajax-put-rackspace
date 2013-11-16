# vim: set expandtab ts=4 sw=4 syntax=python fileencoding=utf8:

import argparse
import logging
import uuid
import wsgiref.simple_server

import pyrax

log = logging.getLogger('apfur')

def parse_args():

    ap = argparse.ArgumentParser()

    ap.add_argument('rackspace_username')
    ap.add_argument('rackspace_API_key')

    return ap.parse_args()

def serve_upload_page(upload_url, download_url):

    class MyApp(object):

        def __init__(self, upload_url, download_url):
            self.upload_url = upload_url
            self.download_url = download_url

        def render_upload_page(self):

            page = open('./upload-1.html').read()

            return page.format(
                upload_url=self.upload_url,
                download_url=self.download_url)

        def __call__(self, environ, start_response):

            start_response('200 OK', [])
            return [self.render_upload_page()]

    app = MyApp(upload_url, download_url)
    s = wsgiref.simple_server.make_server('', 8765, app)

    logging.info("About to fire up the wsgi server...")
    s.serve_forever()


if __name__ == '__main__':

    args = parse_args()

    logging.basicConfig(level=logging.DEBUG)

    log.info('Configured logging.')

    # Give credentials to pyrax.

    pyrax.set_setting('identity_type',  'rackspace')

    pyrax.set_credentials(
        args.rackspace_username,
        args.rackspace_API_key,
        region="ORD")

    logging.info("Set settings and credentials on pyrax")

    # Now make a container for us to upload to.

    # It is safe to run create_container even if the container already
    # exists.
    uploads_container = pyrax.cloudfiles.create_container('uploads')

    uploads_container.set_metadata({
        'Access-Control-Allow-Origin': 'http://localhost:8765'})

    filename = str(uuid.uuid4())

    log.info("File will be stored with name {0}.".format(filename))

    upload_url = pyrax.cloudfiles.get_temp_url(
        uploads_container, filename, 60*60, method='PUT')

    log.debug('upload_url: {0}'.format(upload_url))

    download_url = pyrax.cloudfiles.get_temp_url(
        uploads_container, filename, 60*60, method='GET')

    log.debug('download_url: {0}'.format(download_url))

    serve_upload_page(upload_url, download_url)
