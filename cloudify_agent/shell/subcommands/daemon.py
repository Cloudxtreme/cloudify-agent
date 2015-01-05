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

import click
from cloudify.utils import setup_default_logger

from cloudify_agent.api import daemon as daemon_api
from cloudify_agent.shell import env


shell_logger = setup_default_logger(
    logger_name='shell.cloudify.agent.daemon',
    fmt='%(message)s'
)


def _help(message, envvar_name):
    return '{0}. Configurable via the {1} ' \
           'environment variable.'\
           .format(message, envvar_name)


@click.command()
@click.option('--queue',
              help=_help('The name of the queue to register the agent to',
                         env.CLOUDIFY_DAEMON_QUEUE),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_QUEUE)
@click.option('--ip',
              help=_help('A resolvable IP address for this host',
                         env.CLOUDIFY_AGENT_IP),
              required=True,
              envvar=env.CLOUDIFY_AGENT_IP)
@click.option('--manager-ip',
              help=_help('The manager IP to connect to',
                         env.CLOUDIFY_MANAGER_IP),
              required=True,
              envvar=env.CLOUDIFY_MANAGER_IP)
@click.option('--user',
              help=_help('The user to create this daemon under',
                         env.CLOUDIFY_DAEMON_USER),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_USER)
@click.option('--group',
              help=_help('The group to create this daemon under. If not specified, '
                         'it will have the same value as the --user option',
                         env.CLOUDIFY_DAEMON_GROUP),
              envvar=env.CLOUDIFY_DAEMON_GROUP)
@click.option('--basedir',
              help=_help('Base directory for runtime files (pid, log). '
                         'Defaults to current working directory.',
                         env.CLOUDIFY_DAEMON_BASEDIR),
              envvar=env.CLOUDIFY_DAEMON_BASEDIR)
@click.option('--broker-ip',
              help=_help('The broker ip to connect to. If not specified, the --manager_ip '
                         'option will be used.',
                         env.CLOUDIFY_BROKER_IP),
              envvar=env.CLOUDIFY_BROKER_IP)
@click.option('--broker-port',
              help=_help('The broker port to connect to.',
                         env.CLOUDIFY_BROKER_PORT),
              envvar=env.CLOUDIFY_BROKER_PORT)
@click.option('--manager-port',
              help=_help('The manager REST gateway port to connect to.',
                         env.CLOUDIFY_MANAGER_PORT),
              envvar=env.CLOUDIFY_MANAGER_PORT)
@click.option('--autoscale',
              help=_help('Autoscale parameters in the form of <minimum,maximum> (e.g 2,5)',
                         env.CLOUDIFY_DAEMON_AUTOSCALE),
              envvar=env.CLOUDIFY_DAEMON_AUTOSCALE)
def create(queue,
           ip,
           manager_ip,
           user,
           group,
           basedir,
           broker_ip,
           broker_port,
           manager_port,
           autoscale):

    """
    Creates the necessary configuration files for the daemon.
    Supported daemon types: [init.d]

    """

    optional_parameters = {
        'group': group,
        'broker_ip': broker_ip,
        'broker_port': broker_port,
        'manager_port': manager_port,
        'autoscale': autoscale,
        'basedir': basedir
    }

    click.secho('Creating...', fg='green')

    daemon = daemon_api.create(
        queue=queue,
        ip=ip,
        manager_ip=manager_ip,
        user=user,
        **optional_parameters
    )
    click.secho('Successfully created {0} daemon'.format(daemon.name), fg='green')


@click.command()
@click.option('--queue',
              help=_help('The queue of the worker for whom to register the plugin.',
                         env.CLOUDIFY_DAEMON_QUEUE),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_QUEUE)
@click.option('--plugin',
              help='The plugin name. As stated in its setup.py file.',
              required=True)
def register(queue, plugin):
    click.secho('Registering...', fg='green')
    daemon_api.register(queue, plugin)
    click.secho('Successfully registered {0} to daemon with queue {1}'
                .format(plugin, queue),
                fg='green')
