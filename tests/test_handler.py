import base64
import json
import os
import time
from mock import patch
from threading import Thread
from rancher_gen.handler import RancherConnector, MessageHandler
from rancher_gen.compat import b64encode


class TestRancherConnector:

    @classmethod
    def setup_class(cls):
        template = os.path.join(os.path.dirname(__file__), 'fixtures',
                                'template.j2')
        cls.out_file = '/tmp/out.txt'
        cls.config = {
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': None,
            'access_key': os.getenv('RANCHER_ACCESS_KEY'),
            'secret_key': os.getenv('RANCHER_SECRET_KEY'),
            'templates': ['{0}:{1}'.format(template, cls.out_file)],
            'ssl': False,
            'stack': 'teststack',
            'services': ['hello1', 'hello2'],
            'notify': None
        }

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.out_file):
            os.remove(cls.out_file)

    def test_prerenders_template(self, stack_service):
        stack, service = stack_service
        self.config['project_id'] = stack['accountId']

        # Test with filtering by stack and service
        handler = RancherConnector(**self.config)
        handler._prerender()
        with open(self.out_file) as fh:
            output = fh.read().replace('\n', '').strip()

        assert '10.42.232.33' in output
        assert '10.42.232.34' in output

        # Test with filtering by stack only
        config = self.config.copy()
        config['project_id'] = stack['accountId']
        config['services'] = None
        handler = RancherConnector(**config)
        handler._prerender()
        with open(self.out_file) as fh:
            output = fh.read().replace('\n', '').strip()

        assert '10.42.232.33' in output
        assert '10.42.232.34' in output

        # Test without filtering
        config = self.config.copy()
        config['project_id'] = stack['accountId']
        config['stack'] = None
        config['services'] = None
        handler = RancherConnector(**config)
        handler._prerender()
        with open(self.out_file) as fh:
            output = fh.read().replace('\n', '').strip()

        assert '10.42.232.33' in output

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
        stack, services = stack_service

        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        api_token = b64encode("{0}:{1}".format(access_key, secret_key))
        template = os.path.join(os.path.dirname(__file__), 'fixtures',
                                'template.j2')
        config = {
            'message': mock_message,
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': stack['accountId'],
            'api_token': api_token,
            'templates': ['{0}:{1}'.format(template, self.out_file)],
            'ssl': False,
            'stack': 'teststack',
            'services': ['hello1', 'hello2'],
            'notify': None
        }

        # Test with stack and service filter
        handler = MessageHandler(**config)
        handler.run()

        while not os.path.exists(self.out_file):
            time.sleep(1)

        with open(self.out_file) as fh:
            output = fh.read().replace('\n', '').strip()

        assert '10.42.232.33' in output
        assert '10.42.232.34' in output

        # Test with stack only filter
        config['project_id'] = stack['accountId']
        config['services'] = None
        handler = MessageHandler(**config)
        handler.run()

        while not os.path.exists(self.out_file):
            time.sleep(1)

        with open(self.out_file) as fh:
            output = fh.read().replace('\n', '').strip()

        assert '10.42.232.33' in output
        assert '10.42.232.34' in output

        # Test without filter
        config['stack'] = None
        handler = MessageHandler(**config)
        handler.run()

        while not os.path.exists(self.out_file):
            time.sleep(1)

        with open(self.out_file) as fh:
            output = fh.read().replace('\n', '').strip()

        assert '10.42.232.33' in output

    def test_does_not_render_with_missing_labels_in_message(
            self, stack_service, mock_message):
        stack, service = stack_service
        mock_message['data']['resource']['labels'] = None

        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        api_token = b64encode("{0}:{1}".format(access_key, secret_key))
        template = os.path.join(os.path.dirname(__file__), 'fixtures',
                                'template.j2')
        config = {
            'message': mock_message,
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': stack['accountId'],
            'api_token': api_token,
            'templates': ['{0}:{1}'.format(template, self.out_file)],
            'ssl': False,
            'stack': 'teststack',
            'services': ['badservice'],
            'notify': None
        }

        handler = MessageHandler(**config)
        handler.run()
        time.sleep(1)
        assert not os.path.exists(self.out_file)

    def test_does_not_render_with_missing_stack_name_in_message(
            self, stack_service, mock_message):
        stack, service = stack_service
        del mock_message['data']['resource']['labels']['io.rancher.stack.name']

        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        api_token = b64encode("{0}:{1}".format(access_key, secret_key))
        template = os.path.join(os.path.dirname(__file__), 'fixtures',
                                'template.j2')
        config = {
            'message': mock_message,
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': stack['accountId'],
            'api_token': api_token,
            'templates': ['{0}:{1}'.format(template, self.out_file)],
            'ssl': False,
            'stack': 'teststack',
            'services': ['badservice'],
            'notify': None
        }

        handler = MessageHandler(**config)
        handler.run()
        time.sleep(1)
        assert not os.path.exists(self.out_file)
        

    def test_does_not_render_with_invalid_filter(
            self, stack_service, mock_message):
        stack, service = stack_service

        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        api_token = b64encode("{0}:{1}".format(access_key, secret_key))
        template = os.path.join(os.path.dirname(__file__), 'fixtures',
                                'template.j2')
        config = {
            'message': mock_message,
            'host': os.getenv('RANCHER_HOST'),
            'port': int(os.getenv('RANCHER_PORT', 80)),
            'project_id': stack['accountId'],
            'api_token': api_token,
            'templates': ['{0}:{1}'.format(template, self.out_file)],
            'ssl': False,
            'ssl': False,
            'stack': 'teststack',
            'services': ['badservice'],
            'notify': None
        }

        # Test with bad service name
        handler1 = MessageHandler(**config)
        handler1.start()
        time.sleep(1)
        assert not os.path.exists(self.out_file)

        # test with back stack name
        config['stack'] = 'bad'
        config['services'] = None

        handler2 = MessageHandler(**config)
        handler2.start()
        time.sleep(1)
        assert not os.path.exists(self.out_file)
