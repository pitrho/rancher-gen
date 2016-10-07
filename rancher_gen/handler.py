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
from .rancher import API

logger = logging.getLogger(__name__)

# Change the log level on the requests library
logging.getLogger("requests").setLevel(logging.WARNING)


class RancherConnector(object):

    def __init__(self, host, port, project_id, access_key, secret_key,
                 template, dest, ssl=False, stack=None, service=None,
                 notify=None):
        self.rancher_host = host
        self.rancher_port = port
        self.project_id = project_id
        self.api_token = b64encode("{0}:{1}".format(access_key, secret_key))
        self.template = template
        self.dest = dest
        self.ssl = ssl
        self.stack = stack
        self.service = service
        self.notify = notify

    def __call__(self):
        self._prerender()
        self.start()

    def _prerender(self):
        instances = None
        api = API(self.rancher_host, self.rancher_port, self.project_id,
                  self.api_token, self.ssl)

        # If we're not filtering by stack and service, then load all instances
        # in the environment
        if self.stack is None and self.service is None:
            instances = api.get_instances()

        # If we're only filterting by stack, then load the instances for that
        # stack
        elif self.stack and self.service is None:
            instances = api.get_instances(stack_name=self.stack)

        # If we're filtering by stack and service, then load the instances for
        # that service
        elif self.stack and self.service:
            api = API(self.rancher_host, self.rancher_port, self.project_id,
                      self.api_token, self.ssl)
            service = api.get_service(resource=None, stack=self.stack,
                                      service=self.service)
            if service:
                instances = api.get_instances(service)

        # If we found any instnaces, then render the template
        if instances is None:
            instances = []

        render_template(instances, self.template, self.dest)
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
                                     self.template, self.dest, self.ssl,
                                     self.stack, self.service, self.notify)
            handler.start()


class MessageHandler(Thread):
    def __init__(self, message, host, port, project_id, api_token, template,
                 dest, ssl, stack=None, service=None, notify=None):
        Thread.__init__(self)
        self.message = message
        self.rancher_host = host
        self.rancher_port = port
        self.project_id = project_id
        self.api_token = api_token
        self.template = template
        self.dest = dest
        self.ssl = ssl
        self.stack = stack
        self.service = service
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
                service_and_name = '{0}/{1}'.format(self.stack, self.service)

                # If we're filtering by service, then load the instances for
                # this sevice
                if self.service:
                    if service_name != service_and_name:
                        return

                    service = api.get_service(resource)
                    if service:
                        instances = api.get_instances(service)
                        self._render_and_notify(instances)
                        return

                # If we're filtering only by stack, get the intances in the
                # stack
                if stack_name != self.stack:
                    return
                instances = api.get_instances(stack_name=self.stack)
                self._render_and_notify(instances)
            else:
                instances = api.get_instances()
                self._render_and_notify(instances)

    def _render_and_notify(self, instances):
        if instances is None:
            render_template([], self.template, self.dest)
        else:
            render_template(instances, self.template, self.dest)
        notify(self.notify)


def render_template(instances, template, dest):
    template_dir = os.path.dirname(template)
    template_filename = os.path.basename(template)
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
