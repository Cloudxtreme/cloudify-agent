#########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

import sys
import argparse
from celery.__main__ import main as celery_main


def main():

    if 'daemonize' in sys.argv:

        # Use argparse to parse arguments for the
        # daemonize command

        args = _parse_daemonize_args(sys.argv[2:])
        args.handler(args)

    else:

        # only other option is to directly delegate
        # to celery command line.

        sys.argv[0] = 'celery'
        celery_main()


def _daemonize(args):
    env_file_path = args.env_file_path
    print env_file_path


def _parse_daemonize_args(args):
    parser = argparse.ArgumentParser(
        'cfy-agent daemonize',
        description='Daemonize a cfy-agent. '
                    'Currently only support /etc/init.d daemons.')

    parser.add_argument('--user',
                        dest='user',
                        help='The user this agent will start under.')

    parser.add_argument('--broker-ip',
                        dest='broker_ip',
                        help='IP address of the broker to connect to.',
                        default='localhost')

    parser.add_argument('--agent-ip',
                        dest='agent_ip',
                        help='The internal IP address of the machine.',
                        default='127.0.0.1')

    parser.add_argument('--queue',
                        dest='queue',
                        help='The queue name this agent should register to.')

    parser.add_argument('--auto-scale',
                        dest='auto_scale',
                        help='The auto scaling parameters in the form of <minimum,maximum> (e.g 2,5)')

    parser.set_defaults(handler=_daemonize)
    return parser.parse_args(args)