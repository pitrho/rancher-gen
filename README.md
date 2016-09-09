```
8888888b.                             888                             .d8888b.                    
888   Y88b                            888                            d88P  Y88b                   
888    888                            888                            888    888                   
888   d88P  8888b.  88888b.   .d8888b 88888b.   .d88b.  888d888      888         .d88b.  88888b.  
8888888P"      "88b 888 "88b d88P"    888 "88b d8P  Y8b 888P"        888  88888 d8P  Y8b 888 "88b
888 T88b   .d888888 888  888 888      888  888 88888888 888   888888 888    888 88888888 888  888
888  T88b  888  888 888  888 Y88b.    888  888 Y8b.     888          Y88b  d88P Y8b.     888  888
888   T88b "Y888888 888  888  "Y8888P 888  888  "Y8888  888           "Y8888P88  "Y8888  888  888
```

File generator that renders templates using Rancher API. Inspired by
[docker-gen](https://github.com/jwilder/docker-gen).

This program listens for changes on Rancher services and renders a
[Jinja2](http://jinja.pocoo.org/docs/dev/) template. It also has the ability
no run a notification command after the template has been rendered. This could
be useful for generating configuration files for services like Nginx.

## Installation

    pip install rancher-gen


## How to use rancher-gen

```
usage: rancher-gen [--host HOST] [--port PORT] [--access-key ACCESS_KEY]
                   [--secret-key SECRET_KEY] [--project-id PROJECT_ID] [-h]
                   [--log-level {DEBUG,INFO,WARNING,CRITICAL,ERROR}]
                   [--stack STACK] [--service SERVICE] [--ssl]
                   [--notify NOTIFY]
                   template dest

Generate files from rancher meta-data

positional arguments:
  template              Path to template to generate
  dest                  Output path for generated file

named arguments:
  --host HOST           Rancher host (defaults to localhost)
  --port PORT           Rancher port (defaults to 80 or 443 if ssl is
                        specified)
  --access-key ACCESS_KEY
                        The Rancher access key
  --secret-key SECRET_KEY
                        The Rancher secret key
  --project-id PROJECT_ID
                        Rancher's project id

optional arguments:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,CRITICAL,ERROR}
                        Set the log level.
  --stack STACK         The name of the rancher stack
  --service SERVICE     The name of the rancher service
  --ssl                 User secure connections (https and wss)
  --notify NOTIFY       Command to run after template is generated (e.g
                        restart some-service)

```

In order to run rancher-gen, you must specify at least the following parameters:
  * host: The ip/dns name of the rancher server.
  * port: The port of the rancher server. It defaults to 80 or 443 for SSL.
  * access-key: The access key to access the Rancher server.
  * secret-key: The secret key to access the Rancher server.
  * proejct-id: The project id (environment) from Rancher.

## What's passed to the templates
A list of container instances is passed to the template when is rendered. So,
you can do something like:

    {% for container in containers %}
      {{container['primaryIpAddress']}}
    {% endfor %}

### Example of container data that is being passed to the template

```
{
  "id": "1i258",
  "type": "container",
  "links": {
    "self": "…/v1/projects/1a5/containers/1i258",
    "account": "…/v1/projects/1a5/containers/1i258/account",
    "credentials": "…/v1/projects/1a5/containers/1i258/credentials",
    "healthcheckInstanceHostMaps": "…/v1/projects/1a5/containers/1i258/healthcheckinstancehostmaps",
    "hosts": "…/v1/projects/1a5/containers/1i258/hosts",
    "instanceLabels": "…/v1/projects/1a5/containers/1i258/instancelabels",
    "instanceLinks": "…/v1/projects/1a5/containers/1i258/instancelinks",
    "instances": "…/v1/projects/1a5/containers/1i258/instances",
    "mounts": "…/v1/projects/1a5/containers/1i258/mounts",
    "ports": "…/v1/projects/1a5/containers/1i258/ports",
    "serviceEvents": "…/v1/projects/1a5/containers/1i258/serviceevents",
    "serviceExposeMaps": "…/v1/projects/1a5/containers/1i258/serviceexposemaps",
    "services": "…/v1/projects/1a5/containers/1i258/services",
    "targetInstanceLinks": "…/v1/projects/1a5/containers/1i258/targetinstancelinks",
    "volumes": "…/v1/projects/1a5/containers/1i258/volumes",
    "stats": "…/v1/projects/1a5/containers/1i258/stats",
    "containerStats": "…/v1/projects/1a5/containers/1i258/containerstats",
  },
  "actions": {
    "update": "…/v1/projects/1a5/containers/1i258/?action=update",
    "stop": "…/v1/projects/1a5/containers/1i258/?action=stop",
    "restart": "…/v1/projects/1a5/containers/1i258/?action=restart",
    "migrate": "…/v1/projects/1a5/containers/1i258/?action=migrate",
    "logs": "…/v1/projects/1a5/containers/1i258/?action=logs",
    "setlabels": "…/v1/projects/1a5/containers/1i258/?action=setlabels",
    "execute": "…/v1/projects/1a5/containers/1i258/?action=execute",
    "proxy": "…/v1/projects/1a5/containers/1i258/?action=proxy",
  },
  "name": "foo_nginx2_1",
  "state": "running",
  "accountId": "1a5",
  "blkioDeviceOptions": null,
  "build": null,
  "capAdd": null,
  "capDrop": null,
  "command": null,
  "cpuSet": null,
  "cpuShares": null,
  "createIndex": 1,
  "created": "2016-09-07T01:37:19Z",
  "createdTS": 1473212239000,
  "dataVolumeMounts": {},
  "dataVolumes": [
    "/tmp/nginxconf:/nginxconf",
  ],
  "dataVolumesFrom": null,
  "deploymentUnitUuid": "e4af719b-39ad-4576-8402-8a29a6ec97d6",
  "description": null,
  "devices": null,
  "dns": [
    "169.254.169.250",
  ],
  "dnsSearch": [
    3items"foo.rancher.internal",
    "nginx2.foo.rancher.internal",
    "rancher.internal",
  ],
  "domainName": null,
  "entryPoint": null,
  "environment": {
    "NGINX_RUN_TYPE": "rancher-gen",
    "RANCHER_GEN_ACCESS_KEY": "37AF1F5CD18843DF00CC",
    "RANCHER_GEN_HOST": "192.168.0.15",
    "RANCHER_GEN_OPTIONS": "--port 8080 --stack foo --service hello",
    "RANCHER_GEN_PROJECT_ID": "1a5",
    "RANCHER_GEN_SECRET_KEY": "7D7Bio7bcK1vGbj5jNGVCnAEZFrnmZXPjaEZ8Fs2",
  },
  "expose": null,
  "externalId": "f61757f4ede26d6bbbb2ddc31aa8b17dd4227a3bbca12225ddab66e77d76971d",
  "extraHosts": null,
  "firstRunning": "2016-09-07T01:37:20Z",
  "firstRunningTS": 1473212240000,
  "healthCheck": null,
  "healthState": null,
  "hostId": "1h2",
  "hostname": null,
  "imageUuid": "docker:pitrho/nginx:dev",
  "kind": "container",
  "labels": {
    "io.rancher.project.name": "foo",
    "io.rancher.service.deployment.unit": "e4af719b-39ad-4576-8402-8a29a6ec97d6",
    "io.rancher.service.launch.config": "io.rancher.service.primary.launch.config",
    "io.rancher.project_service.name": "foo/nginx2",
    "io.rancher.stack.name": "foo",
    "io.rancher.stack_service.name": "foo/nginx2",
    "io.rancher.service.hash": "ddf05372f057253876d50b81c26eb1a350438d49",
    "io.rancher.container.uuid": "90028a61-6fd5-460a-a8b7-f90bcaf664f2",
    "io.rancher.container.name": "foo_nginx2_1",
    "io.rancher.container.ip": "10.42.172.71/16",
  },
  "logConfig": {},
  "lxcConf": null,
  "memory": null,
  "memorySwap": null,
  "nativeContainer": false,
  "networkContainerId": null,
  "networkMode": "managed",
  "pidMode": null,
  "ports": [
    "80:80/tcp",
  ],
  "primaryIpAddress": "10.42.172.71",
  "privileged": false,
  "publishAllPorts": false,
  "readOnly": false,
  "registryCredentialId": null,
  "removed": null,
  "requestedHostId": null,
  "restartPolicy": null,
  "securityOpt": null,
  "startCount": 1,
  "startOnCreate": true,
  "stdinOpen": false,
  "systemContainer": null,
  "transitioning": "no",
  "transitioningMessage": null,
  "transitioningProgress": null,
  "tty": false,
  "user": null,
  "uuid": "90028a61-6fd5-460a-a8b7-f90bcaf664f2",
  "version": "0",
  "volumeDriver": null,
  "workingDir": null,
}
```


## Examples

### Listening for changes at the project level

    rancher-gen --host rancher.mycompany.com --port 8080 --access-key 1234567890 --secret-key 123ABC456DEF789GHI --project-id 1a5 /tmp/template.j2 /tmp/output.txt

### Listening for changes at the stack level

    rancher-gen --host rancher.mycompany.com --port 8080 --access-key 1234567890 --secret-key 123ABC456DEF789GHI --project-id 1a5 --stack mystack /tmp/template.j2 /tmp/output.txt

### Listening for changes at the service level

    rancher-gen --host rancher.mycompany.com --port 8080 --access-key 1234567890 --secret-key 123ABC456DEF789GHI --project-id 1a5 --stack mystack --service myservice /tmp/template.j2 /tmp/output.txt

### Using secure connections

    rancher-gen --host rancher.mycompany.com --access-key 1234567890 --secret-key 123ABC456DEF789GHI --project-id 1a5 --stack mystack --service myservice --ssl /tmp/template.j2 /tmp/output.txt

### Creating nginx config and reloading (notify)

    rancher-gen --host rancher.mycompany.com --port 8080 --access-key 1234567890 --secret-key 123ABC456DEF789GHI --project-id 1a5 --stack mystack --service myservice --ssl --notify "service nginx reload" /tmp/default.tmpl /etc/nginx/sites-enabled/default

## License
MIT
