from __future__ import absolute_import

import json
import logging
import os
import requests
import ssl
import websocket

from jinja2 import Environment, FileSystemLoader
from subprocess import call
from threading import Thread

from .compat import b64encode
from .exception import RancherConnectionError
from .rancher import API

logger = logging.getLogger(__name__)

# Change the log level on the requests library
logging.getLogger("requests").setLevel(logging.WARNING)


class RancherConnector(object):

    def __init__(self, host, port, project_id, access_key, secret_key,
                 templates, ssl=False, stack=None, services=None,
                 notify=None):
        self.rancher_host = host
        self.rancher_port = port
        self.project_id = project_id
        self.api_token = b64encode("{0}:{1}".format(access_key, secret_key))
        self.templates = templates
        self.ssl = ssl
        self.stack = stack
        self.services = services
        self.notify = notify

    def __call__(self):
        self._prerender()
        self.start()

    def _prerender(self):
        instances = None
        api = API(self.rancher_host, self.rancher_port, self.project_id,
                  self.api_token, self.ssl)

        try:
            # If we're not filtering by stack and services, then load all instances
            # in the environment
            if self.stack is None and self.services is None:
                instances = api.get_instances()

            # If we're only filterting by stack, then load the instances for that
            # stack
            elif self.stack and self.services is None:
                instances = api.get_instances(stack_name=self.stack)

            # If we're filtering by stack and service, then load the instances for
            # that service
            elif self.stack and self.services and len(self.services) > 0:
                api = API(self.rancher_host, self.rancher_port, self.project_id,
                        self.api_token, self.ssl)
                services = api.get_services(self.stack, self.services)

                instances = []
                if len(services) > 0:
                    for service in services:
                        instances += api.get_instances(service)
        except RancherConnectionError:
            # If we made it here, it means we couldn't connect to rancher,
            # so simply return
            return

        # If we found any instances, then render the templates
        if instances is None:
            instances = []
        render_templates(instances, self.templates)
        notify(self.notify)

    def start(self):
        header = {
            'Authorization': 'Basic {0}'.format(self.api_token)
        }
        protocol = 'wss' if self.ssl else 'ws'
        url = '{0}://{1}:{2}/v1/projects/{3}/subscribe?eventNames='\
            'resource.change&include=services'\
            .format(protocol, self.rancher_host, self.rancher_port,
                    self.project_id)
        self.ws = websocket.WebSocketApp(url, header=header,
                                         on_message=self._on_message,
                                         on_open=self._on_open,
                                         on_error=self._on_error,
                                         on_close=self._on_close)

        logger.info('Watching for rancher events')
        self.ws.run_forever()

    def _on_open(self, ws):  # pragma: no cover
        logger.info("Websocket connection open")

    def _on_close(self, ws):  # pragma: no cover
        logger.info('Websocket connection closed')

    def _on_error(self, ws, error):  # pragma: no cover
        logger.error(error)

    def _on_message(self, ws, message):
        msg = json.loads(message)
        if msg['name'] == 'resource.change' and msg['data']:
            handler = MessageHandler(msg, self.rancher_host, self.rancher_port,
                                     self.project_id, self.api_token,
                                     self.templates, self.ssl,
                                     self.stack, self.services, self.notify)
            handler.start()


class MessageHandler(Thread):
    def __init__(self, message, host, port, project_id, api_token, templates,
                 ssl, stack=None, services=None, notify=None):
        Thread.__init__(self)
        self.message = message
        self.rancher_host = host
        self.rancher_port = port
        self.project_id = project_id
        self.api_token = api_token
        self.templates = templates
        self.ssl = ssl
        self.stack = stack
        self.services = services
        self.notify = notify

    def run(self):
        resource = self.message['data']['resource']
        if resource['type'] == 'container' and \
                resource['state'] in ['running', 'removed', 'stopped']:

            api = API(self.rancher_host, self.rancher_port, self.project_id,
                      self.api_token, self.ssl)

            # Filter by stack and/or service name if specified
            if self.stack:
                # Some instnaces like Network Agents don't have labels, and
                # don't really belong to a stack and/or service, so if this
                # message has to do with one of those instances, then we
                # need to ignore it.
                if resource['labels'] is None:
                    return

                stack_name = resource['labels']['io.rancher.stack.name']
                service_name =\
                    resource['labels']['io.rancher.stack_service.name']
                service_name = service_name.split('/')[1]

                # if the stacks don't match, then simply return
                if stack_name != self.stack:
                    return

                # If we're filtering by service, then load the instances for
                # this sevice
                if self.services and len(self.services) > 0:
                    if service_name not in self.services:
                        return

                    services = api.get_services(self.stack, self.services)
                    instances = []
                    if len(services) > 0:
                        for service in services:
                            instances += api.get_instances(service)
                        self._render_and_notify(instances)
                        return

                instances = api.get_instances(stack_name=self.stack)
                self._render_and_notify(instances)
            else:
                instances = api.get_instances()
                self._render_and_notify(instances)

    def _render_and_notify(self, instances):
        if instances is None:
            render_templates([], self.templates)
        else:
            render_templates(instances, self.templates)
        notify(self.notify)


def render_templates(instances, templates):
    for template in templates:
        source, dest = template.split(':')

        template_dir = os.path.dirname(source)
        template_filename = os.path.basename(source)
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_filename)
        result = template.render(containers=instances)

        with open(dest, 'w') as fh:
            fh.write(result)
        logger.info("Generated '{0}'".format(dest))


def notify(notify):
    if notify:
        logger.info("Running '{0}'".format(notify))
        call(notify, shell=True)
