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

from cloudify_agent.api import defaults
from cloudify_agent.shell import env
from cloudify_agent.api.daemon.factory import DaemonFactory


@click.command()
@click.option('--name',
              help='The name of the daemon. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_NAME),
              envvar=env.CLOUDIFY_DAEMON_NAME)
@click.option('--queue',
              help='The name of the queue to register the agent to. [env {0}]'
                   .format(env.CLOUDIFY_DAEMON_QUEUE),
              envvar=env.CLOUDIFY_DAEMON_QUEUE)
@click.option('--host',
              help='A resolvable IP address for this host. [env {0}]'
                   .format(env.CLOUDIFY_AGENT_HOST),
              envvar=env.CLOUDIFY_AGENT_HOST)
@click.option('--manager-ip',
              help='The manager IP to connect to. [env {0}]'
                   .format(env.CLOUDIFY_MANAGER_IP),
              required=True,
              envvar=env.CLOUDIFY_MANAGER_IP)
@click.option('--user',
              help='The user to create this daemon under. [env {0}]'
                   .format(env.CLOUDIFY_DAEMON_USER),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_USER)
@click.option('--workdir',
              help='Working directory for runtime files (pid, log). '
                   'Defaults to current working directory. [env {0}]'
                   .format(env.CLOUDIFY_DAEMON_BASEDIR),
              envvar=env.CLOUDIFY_DAEMON_BASEDIR)
@click.option('--broker-ip',
              help='The broker ip to connect to. '
                   'If not specified, the --manager_ip '
                   'option will be used. [{0}]'
                   .format(env.CLOUDIFY_BROKER_IP),
              envvar=env.CLOUDIFY_BROKER_IP)
@click.option('--broker-port',
              help='The broker port to connect to. [env {0}]'
                   .format(env.CLOUDIFY_BROKER_PORT),
              envvar=env.CLOUDIFY_BROKER_PORT)
@click.option('--broker-url',
              help='The broker url to connect to. If this '
                   'option is specified, the broker-ip and '
                   'broker-port options are ignored. [env {0}]'
              .format(env.CLOUDIFY_BROKER_URL),
              envvar=env.CLOUDIFY_BROKER_URL)
@click.option('--manager-port',
              help='The manager REST gateway port to connect to. [env {0}]'
                   .format(env.CLOUDIFY_MANAGER_PORT),
              envvar=env.CLOUDIFY_MANAGER_PORT)
@click.option('--min-workers',
              help='Minimum number of workers for '
                   'the autoscale configuration. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_MIN_WORKERS),
              envvar=env.CLOUDIFY_DAEMON_MIN_WORKERS)
@click.option('--max-workers',
              help='Maximum number of workers for '
                   'the autoscale configuration. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_MAX_WORKERS),
              envvar=env.CLOUDIFY_DAEMON_MAX_WORKERS)
@click.option('--disable-requiretty/--no-disable-requiretty',
              help='Disables the requiretty directive in the sudoers file. ['
                   'env {0}]'
              .format(env.CLOUDIFY_DAEMON_DISABLE_REQUIRETTY),
              default=False,
              envvar=env.CLOUDIFY_DAEMON_DISABLE_REQUIRETTY)
@click.option('--relocated/--no-relocated',
              help='Indication that this virtualenv was relocated. '
                   'If this option is passed, an auto-correction '
                   'to the virtualenv shabang entries '
                   'will be performed [env {0}]'
              .format(env.CLOUDIFY_RELOCATED),
              default=False,
              envvar=env.CLOUDIFY_RELOCATED)
@click.option('--process-management',
              help='The process management system to use '
                   'when creating the daemon. [env {0}]'
                   .format(env.CLOUDIFY_DAEMON_PROCESS_MANAGEMENT),
              type=click.Choice(['init.d']),
              default='init.d',
              envvar=env.CLOUDIFY_DAEMON_PROCESS_MANAGEMENT)
def create(process_management, **params):

    """
    Creates the necessary configuration files for the daemon.

    """

    click.echo('Creating...')
    daemon = DaemonFactory.new(
        process_management=process_management,
        **params
    )
    daemon.create()
    DaemonFactory.save(daemon)
    click.echo('Successfully created daemon: {0}'
               .format(daemon.name))


@click.command()
@click.option('--name',
              help='The name of the daemon. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_NAME),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_NAME)
@click.option('--plugin',
              help='The plugin name. As stated in its setup.py file.',
              required=True)
def register(name, plugin):

    """
    Registers an additional plugin. All methods decorated with the 'operation'
    decorator inside plugin modules will be imported.

    """

    click.echo('Registering...')
    daemon = DaemonFactory.load(name)
    daemon.register(plugin)
    click.echo('Successfully registered {0} with daemon: {1}'
               .format(plugin, name))


@click.command()
@click.option('--name',
              help='The name of the daemon. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_NAME),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_NAME)
@click.option('--interval',
              help='The interval in seconds to sleep when waiting '
                   'for the daemon to be ready.',
              default=defaults.START_INTERVAL)
@click.option('--timeout',
              help='The timeout in seconds to wait '
                   'for the daemon to be ready.',
              default=defaults.START_TIMEOUT)
def start(name, interval, timeout):

    """
    Starts the daemon.

    """

    click.echo('Starting...')
    daemon = DaemonFactory.load(name)
    daemon.start(
        interval=interval,
        timeout=timeout
    )
    click.echo('Successfully started daemon: {0}'.format(name))


@click.command()
@click.option('--name',
              help='The name of the daemon. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_NAME),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_NAME)
@click.option('--interval',
              help='The interval in seconds to sleep when waiting '
                   'for the daemon to stop.',
              default=defaults.STOP_INTERVAL)
@click.option('--timeout',
              help='The timeout in seconds to wait '
                   'for the daemon to stop.',
              default=defaults.STOP_TIMEOUT)
def stop(name, interval, timeout):

    """
    Stops the daemon.

    """

    click.echo('Stopping...')
    daemon = DaemonFactory.load(name)
    daemon.stop(
        interval=interval,
        timeout=timeout
    )
    click.secho('Successfully stopped daemon: {0}'.format(name))


@click.command()
@click.option('--name',
              help='The name of the daemon. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_NAME),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_NAME)
def restart(name):

    """
    Restarts the daemon.

    """

    click.echo('Restarting...')
    daemon = DaemonFactory.load(name)
    daemon.restart()
    click.echo('Successfully restarted daemon: {0}'.format(name))


@click.command()
@click.option('--name',
              help='The name of the daemon. [env {0}]'
              .format(env.CLOUDIFY_DAEMON_NAME),
              required=True,
              envvar=env.CLOUDIFY_DAEMON_NAME)
def delete(name):

    """
    Deletes the daemon.

    """

    click.echo('Deleting...')
    daemon = DaemonFactory.load(name)
    daemon.delete()
    DaemonFactory.delete(name)
    click.secho('Successfully deleted daemon: {0}'.format(name))
