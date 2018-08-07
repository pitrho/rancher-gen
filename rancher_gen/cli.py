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

    if not args.templates and (not args.template or not args.dest):
        print ("error: Missing at least one template and destination parameter")
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
    named_args.add_argument('--template', action="append", dest="templates",
                            help="From and To paths of template to render. "
                            "(e.g '/tom/template:/to/file)")

    optional_args = parser.add_argument_group('optional arguments')
    optional_args.add_argument("-h", "--help", action="help",
                               help="show this help message and exit")
    optional_args.add_argument('--log-level', action=SetLogLevel,
                               default='INFO', choices=LOG_LEVELS,
                               help='Set the log level.')
    optional_args.add_argument('--stack',
                               help="The name of the rancher stack")
    optional_args.add_argument('--service', action="append", metavar="SERVICE",
                               dest="services",
                               help="The name of the rancher service")
    optional_args.add_argument('--ssl', action='store_true',
                               default=False,
                               help='User secure connections')
    optional_args.add_argument('--notify',
                               help="Command to run after template is "\
                               "generated (e.g restart some-service)")

    parser.add_argument('template', nargs='?', default=None,
                        help="Path to template to generate. "\
                        "(Deprecated, use --template instead)")
    parser.add_argument('dest', nargs='?', default=None,
                        help="Output path for generated file. "\
                        "(Deprecated, use --template instead)")

    args = parser.parse_args()
    if not validate_args(args):
        return

    templates = args.templates
    if templates is None:
        templates = []
    
    if args.template and args.dest:
        templates.append('{0}:{1}'.format(args.template, args.dest))

    try:
        port = args.port
        if args.port == -1:
            port = 443 if args.ssl else 80
        handler = RancherConnector(args.host, port, args.project_id,
                                   args.access_key, args.secret_key,
                                   templates, args.ssl,
                                   args.stack, args.services, args.notify)
        handler()
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
