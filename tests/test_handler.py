import base64
import json
import StringIO
import os
import time
from mock import patch
from threading import Thread
from rancher_gen.handler import RancherConnector, MessageHandler


class TestRancherConnector:

    @classmethod
    def setup_class(cls):
        cls.out_file = '/tmp/out.txt'
        cls.config = {
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': None,
            'access_key': os.getenv('RANCHER_ACCESS_KEY'),
            'secret_key': os.getenv('RANCHER_SECRET_KEY'),
            'template': os.path.join(os.path.dirname(__file__), 'fixtures',
                                     'template.j2'),
            'dest': cls.out_file,
            'ssl': False,
            'stack': 'teststack',
            'service': 'hello',
            'notify': None
        }

    @classmethod
    def teardown_class(cls):
        os.remove(cls.out_file)

    def test_prerenders_template(self, stack_service):
        stack, service = stack_service
        self.config['project_id'] = stack['accountId']

        handler = RancherConnector(**self.config)
        handler._prerender()
        with open(self.out_file) as fh:
            output = fh.read()

        assert output == '10.42.232.33;'

    def test_on_message_ignores_bad_messages(self):
        handler = RancherConnector(**self.config)
        mock_msg = {
            'name': 'bad',
            'data': []
        }

        # Test with bad name
        with patch.object(MessageHandler, 'run') as mock:
            handler._on_message(None, json.dumps(mock_msg))
        assert not mock.called

        # Test with missing data
        mock_msg['name'] = 'resource.change'
        with patch.object(MessageHandler, 'run') as mock:
            handler._on_message(None, json.dumps(mock_msg))
        assert not mock.called

    def test_on_message_calls_handler(self):
        handler = RancherConnector(**self.config)
        mock_msg = {
            'name': 'resource.change',
            'data': [1, 2, 3]
        }

        with patch.object(MessageHandler, 'run') as mock:
            handler._on_message(None, json.dumps(mock_msg))
        assert mock.called


class TestMessageHandler:

    def setup_method(self, method):
        self.out_file = '/tmp/out.txt'

    def teardown_method(self, method):
        if os.path.exists(self.out_file):
            os.remove(self.out_file)

    def test_renders_template(self, stack_service, mock_message):
        stac, service = stack_service

        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        api_token = base64.b64encode("{0}:{1}".format(access_key, secret_key))
        config = {
            'message': mock_message,
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': None,
            'api_token': api_token,
            'template': os.path.join(os.path.dirname(__file__), 'fixtures',
                                     'template.j2'),
            'dest': self.out_file,
            'ssl': False,
            'stack': 'teststack',
            'service': 'hello',
            'notify': None
        }

        handler = MessageHandler(**config)
        handler.start()

        while not os.path.exists(self.out_file):
            time.sleep(1)

        with open(self.out_file) as fh:
            output = fh.read()

        assert output == '10.42.232.33;'

    def test_does_not_render_with_invalid_filter(
            self, stack_service, mock_message):
        stac, service = stack_service

        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        api_token = base64.b64encode("{0}:{1}".format(access_key, secret_key))
        config = {
            'message': mock_message,
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': None,
            'api_token': api_token,
            'template': os.path.join(os.path.dirname(__file__), 'fixtures',
                                     'template.j2'),
            'dest': self.out_file,
            'ssl': False,
            'stack': 'teststack',
            'service': 'badservice',
            'notify': None
        }

        # Test with bad service name
        handler1 = MessageHandler(**config)
        handler1.start()
        time.sleep(1)
        assert not os.path.exists(self.out_file)

        # test with back stack name
        config['stack'] = 'bad'
        config['service'] = None

        handler2 = MessageHandler(**config)
        handler2.start()
        time.sleep(1)
        assert not os.path.exists(self.out_file)
