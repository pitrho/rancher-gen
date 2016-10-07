from __future__ import absolute_import
import requests


class API(object):

    def __init__(self, host, port, project_id, api_token, ssl):
        self.host = host
        self.port = port
        self.project_id = project_id
        self.api_token = api_token
        self.ssl = ssl
        self._headers = {
            'Authorization': 'Basic {0}'.format(api_token)
        }
        self._protocol = 'https' if ssl else 'http'

    def get_service(self, resource=None, stack=None, service=None):
        """ Get a service from a rancher resource or by stack and name.

        If resource is specified, stack and service and ignore. If resource is
        None, then stack and service are used to lookup the service in Rancher.

        Args:
            - resource: A rancher reource the represents a message sent by the
                web socket.
            - stack: The name of the stack
            - service: The name of the service
        """
        if resource:
            return self._get_service_from_resource(resource)
        elif stack and service:
            return self._get_service_from_stack(stack, service)
        return None

    def get_instances(self, service=None, stack_name=None):
        """ Gets the list of instances from a service.

        If service is specified, it's corresponding links are used to look up
        the intances. If stack_name is specified, it is used used load all
        instances that belong to that stack. If neither service nor stack_name
        are specified, all instances in the environment are returned.

        Args:
            - service: The Rancher object representation of a service
            - stack_name: A stack name
        """
        if service is None:
            url = '{0}://{1}:{2}/v1/projects/{3}/instances'\
                .format(self._protocol, self.host, self.port, self.project_id)
        else:
            url = service['links']['instances']
        res = requests.get(url, headers=self._headers)
        res_data = res.json()
        if res_data['data']:
            if stack_name is None:
                return res_data['data']

            instances = []
            for resource in res_data['data']:
                labels = resource['labels']
                if labels and 'io.rancher.stack.name' in labels and \
                        labels['io.rancher.stack.name'] == stack_name:
                    instances.append(resource)
            if len(instances) > 0:
                return instances

        return None

    def _get_service_from_resource(self, resource):
        # If the state is running or stopped, then the list of services is
        # already part of the resource, so simply return the first service.
        if resource['state'] in ['running', 'stopped']:
            return resource['services'][0]
        elif resource['state'] == 'removed':
            # If a container was removed, we need to search the service by
            # the stack name
            stack_name = resource['labels']['io.rancher.stack.name']
            service_name = resource['labels']['io.rancher.stack_service.name']
            service_name = service_name.split('/')[1]
            return self._get_service_from_stack(stack_name, service_name)
        return None

    def _get_service_from_stack(self, stack_name, service_name):
        # First get the stack
        url = '{0}://{1}:{2}/v1/projects/{3}/environments'\
            .format(self._protocol, self.host, self.port, self.project_id)
        res = requests.get(url, headers=self._headers)
        res_data = res.json()
        service_stack = None
        if res_data['data'] and len(res_data['data']) > 0:
            for stack in res_data['data']:
                if stack['name'] == stack_name:
                    service_stack = stack
                    break

        if not service_stack:
            return None

        url = service_stack['links']['services']
        res = requests.get(url, headers=self._headers)
        res_data = res.json()
        if res_data['data'] and len(res_data['data']) > 0:
            for service in res_data['data']:
                if service['name'] == service_name:
                    return service

        return None
