from __future__ import absolute_import

import json
import os
import pytest
import requests
import time

from rancher_gen.compat import b64encode


@pytest.fixture(scope='session')
def stack_service(request):
    host = os.getenv('RANCHER_HOST')
    port = int(os.getenv('RANCHER_PORT', 80))
    access_key = os.getenv('RANCHER_ACCESS_KEY')
    secret_key = os.getenv('RANCHER_SECRET_KEY')
    api_token = b64encode("{0}:{1}".format(access_key, secret_key))

    with open(os.path.join(os.path.dirname(__file__), 'compose.yaml')) as fh:
        compose_string = fh.read()

    # Create the stack and service
    headers = {
        'Authorization': 'Basic {0}'.format(api_token)
    }
    url = 'http://{0}:{1}/v1/environments'.format(host, port)
    stack_name = 'teststack'
    res = requests.post(url, headers=headers, data={
        'name': stack_name,
        "dockerCompose": compose_string,
        "startOnCreate": True
    })
    stack = res.json()

    # Wait for stack to be active
    state = stack['state']
    url = '{0}?name={1}'.format(url, stack_name)
    while state != 'active':
        res = requests.get(url, headers=headers)
        stack = res.json()['data'][0]
        state = stack['state']
        time.sleep(1)

    # Wait for service to be active
    url = '{0}?name={1}'.format(stack['links']['services'], 'hello')
    res = requests.get(url, headers=headers)
    state = ''
    while state != 'active':
        service = res.json()['data'][0]
        state = service['state']
        time.sleep(1)

    def teardown():
        requests.delete('{0}/{1}'.format(url, stack['id']), headers=headers)
    request.addfinalizer(teardown)

    return stack, service


@pytest.fixture(scope='function')
def mock_message(request, stack_service):
    stack, service = stack_service
    service_id = service['id']
    with open(os.path.join(os.path.dirname(__file__), 'mock_msg.json')) as fh:
        mock_message = json.loads(fh.read())
    instances_link =\
        mock_message['data']['resource']['services'][0]['links']['instances']
    mock_message['data']['resource']['services'][0]['links']['instances'] =\
        instances_link.format(stack['accountId'], service['id'])

    return mock_message
