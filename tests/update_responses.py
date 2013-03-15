# Script for recording responses from the opencenter server as text files.
# These responses will then be used in client tests.


import json
import requests
import sys
import os
import re
import logging
import argparse

sys.path.extend(['libs/httpretty/', '../opencenterclient'])
import tests


class UpdateResponses:

    def __init__(self, argv):

        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--recorddir',
                            default="./recorded-responses",
                            help="Dir to store responses in")
        args = parser.parse_args(argv)

        self.ep = os.environ['OPENCENTER_ENDPOINT']
        self.out_dir = "./recorded-responses"
        self.logger = logging.getLogger("updateresponses")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        if args.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def url_to_filename(self, url):
        file_name = re.sub('[/]', '_', url)
        if file_name.endswith('_'):
            return file_name[:-1]
        return file_name

    def request_and_store(self, method, url, **kwargs):
        self.logger.info('%s %s %s' % (method, url, kwargs))
        if 'data' in kwargs:
            if not 'headers' in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['content-type'] = 'application/json'
        action = getattr(requests, method)
        response = action('%s/%s' % (self.ep, url), **kwargs)
        self.logger.debug(response)
        open(os.path.join(self.out_dir,
                          '%s_%s' % (method, self.url_to_filename(url))),
             'w').write(response.content)
        return response

    def main(self):
        master_schema = self.request_and_store('get', 'schema')
        objects = master_schema.json()['schema']['objects']

        for obj in objects:
            #schemas
            self.request_and_store('get', '%s/schema' % obj)

            #lists
            self.request_and_store('get', '%s/' % obj)

        self.request_and_store('post',
                               'nodes/',
                               data=json.dumps({'name': 'newnode'})
                               )

        for item, args in tests.TestOpenCenterClient.items_to_create.items():
            self.request_and_store('post', '%ss/' %
                                           item, data=json.dumps(args))


if __name__ == "__main__":
    ur = UpdateResponses(sys.argv[1:])
    sys.exit(ur.main())
