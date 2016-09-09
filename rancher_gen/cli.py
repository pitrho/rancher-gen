from __future__ import absolute_import, print_function

import logging
import sys
from argparse import ArgumentParser, Action

from .handler import RancherConnector

logger = logging.getLogger(__name__)

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


class SetLogLevel(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        level = values.upper()
        if level not in LOG_LEVELS:
            raise ValueError("Invalid log level: {0}. Must be one of {1}"
                             .format(values, LOG_LEVELS))
        logging.getLogger('rancher_gen').setLevel(LOG_LEVELS[level])


def validate_args(args):
    if not args.host:
        print ("error: Missing host parameter")
        return False

    if not args.access_key:
        print ("error: Missing Rancher access key parameter")
        return False

    if not args.secret_key:
        print ("error: Missing Rancher secret key parameter")
        return False

    if not args.project_id:
        print ("error: Missing Rancher project id parameter")
        return False

    return True


def main():
    parser = ArgumentParser('rancher-gen', add_help=False,
                            description="Generate files from rancher meta-data")

    named_args = parser.add_argument_group('named arguments')
    named_args.add_argument('--host',
                            help='Rancher host (defaults to localhost)')
    named_args.add_argument('--port', type=int, default=-1,
                            help='Rancher port (defaults to 80 or 443 if ssl '
                            'is specified)')
    named_args.add_argument('--access-key', help='The Rancher access key')
    named_args.add_argument('--secret-key', help='The Rancher secret key')
    named_args.add_argument('--project-id', help="Rancher's project id")

    optional_args = parser.add_argument_group('optional arguments')
    optional_args.add_argument("-h", "--help", action="help",
                               help="show this help message and exit")
    optional_args.add_argument('--log-level', action=SetLogLevel,
                               default='INFO', choices=LOG_LEVELS,
                               help='Set the log level.')
    optional_args.add_argument('--stack',
                               help="The name of the rancher stack")
    optional_args.add_argument('--service',
                               help="The name of the rancher service")
    optional_args.add_argument('--ssl', action='store_true',
                               default=False,
                               help='User secure connections')
    optional_args.add_argument('--notify',
                               help="Command to run after template is "
                               "generated (e.g restart some-service)")

    parser.add_argument('template', help="Path to template to generate")
    parser.add_argument('dest', help="Output path for generated file")

    args = parser.parse_args()
    if not validate_args(args):
        return

    try:
        port = args.port
        if args.port == -1:
            port = 443 if args.ssl else 80
        handler = RancherConnector(args.host, port, args.project_id,
                                   args.access_key, args.secret_key,
                                   args.template, args.dest, args.ssl,
                                   args.stack, args.service, args.notify)
        handler()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
