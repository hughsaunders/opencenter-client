import unittest
import os
import sys
import json
import requests

sys.path.append('./tests/libs/httpretty/')
from httpretty import HTTPretty, httprettified

sys.path.append('opencenterclient')
from opencenterclient import shell


class TestOpenCenterClient(unittest.TestCase):
    items_to_create = {
        'node': {
            'name': 'testnode'
        },
        'task': {
            'node_id': '1',
            'action': 'adventurate',
            'payload': ['payload']
        },
        'adventure': {
            'name': 'testadventure',
            'dsl': ['dsl']
        },
        # 'fact': {
        #     'key': 'newfact',
        #     'node_id': '1'
        # },
        'attr': {
            'node_id': 1,
            'key': 'testattrkey',
            'value': 'testattrvalue'
        }
    }

    def ensure_string(self, input):
        """ensure input is string, convert with json.dumps if not. """
        if not isinstance(input, str):
            return json.dumps(input)
        return input

    def setUp(self):
        HTTPretty.enable()

        # for matcher,entries in HTTPretty._entries.items():
        #     print matcher
        #     for e in entries:
        #         print e

        self.ep = os.environ['OPENCENTER_ENDPOINT']
        self.responses_dir = './tests/recorded-responses'
        self.objects = TestOpenCenterClient.items_to_create.keys()
        #register master schema
        HTTPretty.register_uri(HTTPretty.GET,
                               '%s/schema' % self.ep,
                               body=open(os.path.join(self.responses_dir,
                                                      'get_schema')).read()
                               )

        #register schema and object list for the objects
        for obj in self.objects:
            response_file = '%s/get_%ss' % (self.responses_dir, obj)
            HTTPretty.register_uri(HTTPretty.GET,
                                   '%s/%ss/' % (self.ep, obj),
                                   body=open(response_file, 'r').read()
                                   )

            response_file = '%s/get_%ss_schema' % (self.responses_dir, obj)
            HTTPretty.register_uri(HTTPretty.GET,
                                   '%s/%ss/schema' % (self.ep, obj),
                                   body=open(response_file, 'r').read()
                                   )

            HTTPretty.register_uri(HTTPretty.POST,
                                   '%s/%ss/' % (self.ep, obj),
                                   body=open(os.path.join(self.responses_dir,
                                                          'post_%ss' % obj),
                                             'r').read()
                                   )

        #must be after the initial URIs are registered
        self.opencentershell = shell.OpenCenterShell()

    def test_list_methods(self):
        #print requests.get('%s/tasks/' % self.ep)
        #r = requests.get('%s/schema' % self.ep)
        #print HTTPretty.last_request.__dict__['path']
        for obj in self.objects:
            print "list test: ", obj
            self.opencentershell.main([obj, 'list'])
            req = HTTPretty.last_request
            self.assertEqual(req.__dict__['path'], '/%ss/' % obj)
            self.assertEqual(req.__dict__['method'], 'GET')
            #self.assertEqual(HTTPretty.last_request.headers['url'])
            #print HTTPretty.last_request.headers

    # def test_create_methods(self):
    #
    #     for obj, args in TestOpenCenterClient.items_to_create.items():
    #         print obj, args
    #         self.opencentershell.main([obj, 'create']
    #                              + map(self.ensure_string(args.values())))
    #         req = HTTPretty.last_request
    #         self.assertEqual(req.__dict__['path'], '/%ss/' % obj)
    #         self.assertEqual(req.__dict__['method'], 'POST')

    def tearDown(self):
        HTTPretty.disable()
