import os
from rancher_gen.compat import b64encode
from rancher_gen.rancher import API


class TestAPI:

    def test_get_service(self, stack_service):
        stack, service = stack_service
        host = os.getenv('RANCHER_HOST')
        port = int(os.getenv('RANCHER_PORT', 80))
        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        project_id = stack['accountId']
        api_token = b64encode("{0}:{1}".format(access_key, secret_key))

        api = API(host, port, project_id, api_token, False)

        # Test with stack and service name
        serv = api.get_service(None, stack['name'], "hello")
        assert serv is not None

        # Test with bad stack name
        assert api.get_service(None, 'bad', 'name') is None

        # Test with running resource
        resource = {
            'state': 'running',
            'services': [serv]
        }
        serv = api.get_service(resource)
        assert serv is not None

        # Test with deleted resource
        resource['state'] = 'removed'
        resource['labels'] = {
            'io.rancher.stack.name': stack['name'],
            'io.rancher.stack_service.name': '{0}/{1}'
            .format(stack['name'], 'hello')
        }
        serv = api.get_service(resource)
        assert serv is not None

        # Test with invalid resource state
        assert api.get_service({'state': 'bad'}) is None

        # Test with None values
        assert api.get_service() is None

    def test_get_instances(self, stack_service):
        stack, service = stack_service
        host = os.getenv('RANCHER_HOST')
        port = int(os.getenv('RANCHER_PORT', 80))
        access_key = os.getenv('RANCHER_ACCESS_KEY')
        secret_key = os.getenv('RANCHER_SECRET_KEY')
        project_id = stack['accountId']
        api_token = b64encode("{0}:{1}".format(access_key, secret_key))

        api = API(host, port, project_id, api_token, False)
        serv = api.get_service(None, stack['name'], 'hello')
        instances = api.get_instances(serv)
        assert len(instances) == 1
