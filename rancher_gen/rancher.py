import requests


class API(object):

    def __init__(self, host, port, project_id, api_token, ssl):
        self.host = host
        self.port = port
        self.project_id = project_id
        self.api_token = api_token
        self.ssl = ssl

    def get_service(self, resource=None, stack=None, service=None):
        if resource:
            return self._get_service_from_resource(resource)
        elif stack and service:
            return self._get_service_from_stack(stack, service)
        return None

    def get_instances(self, service):
        headers = {
            'Authorization': 'Basic {0}'.format(self.api_token)
        }
        url = service['links']['instances']
        res = requests.get(url, headers=headers)
        res_data = res.json()
        if res_data['data']:
            return res_data['data']
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
        headers = {
            'Authorization': 'Basic {0}'.format(self.api_token)
        }
        protocol = 'https' if self.ssl else 'http'
        url = '{0}://{1}:{2}/v1/projects/{3}/environments'\
            .format(protocol, self.host, self.port, self.project_id)
        res = requests.get(url, headers=headers)
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
        res = requests.get(url, headers=headers)
        res_data = res.json()
        if res_data['data'] and len(res_data['data']) > 0:
            for service in res_data['data']:
                if service['name'] == service_name:
                    return service

        return None
