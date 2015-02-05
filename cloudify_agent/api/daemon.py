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

from cloudify_agent.api.internal.daemon.factory import DaemonFactory
from cloudify_agent.api import defaults


"""
Public API for a Daemon's lifecycle.
"""


def create(process_management, **params):

    """
    Creates the necessary scripts and configuration files for the daemon.

    The params key-value arguments consist of mandatory and optional keys.

    Mandatory keys are:

    ``name``:

        the name to give the agent. This name will be a unique identifier of the daemon.
        meaning you will not be able to create more agents with that name until a delete
        operation has been performed.

    ``queue``:

        the queue this agent will listen to. It is possible to create different workers with
        the same queue, however this is discouraged. to create more workers that process tasks
        of a given queue, use the 'min_workers' and 'max_workers' key

    ``host``:

        the ip address of the host this agent will run on.

    ``manager_ip``:

        the ip address of the manager host.

    ``user``:

        the user this agent will run under.

    Optional keys are:

    ``workdir``:

        working directory for runtime files (pid, log).
        defaults to the current working directory.

    ``broker_ip``:

        the ip address of the broker to connect to.
        if not specified, the 'manager_ip' key will be used.

    ``broker_port``

        the connection port of the broker process.
        defaults to 5672.

    ``broker_url``:

        full url to the broker. if this key is specified,
        the broker_ip and broker_port keys are ignored.

        for example:
            amqp://192.168.9.19:6786

        if this is not specified, the broker url will be constructed from the
        broker_ip and broker_port like so: 'amqp://guest:guest@<broker_ip>:<broker_port>//'

    ``manager_port``:

        the manager REST gateway port to connect to. defaults to 80.

    ``min_workers``:

        the minimum number of worker processes this agent will manage. all workers will listen on
        the same queue allowing for higher concurrency when preforming tasks.
        defaults to 0.

    ``max_workers``:

        the maximum number of worker processes this agent will manager. as tasks keep coming
        in, the agent will expand its worker pool to handle more tasks concurrently. However, as the name
         suggests, it will never exceed this number. allowing for the control of resource usage.
         defaults to 5.

    ``disable_requiretty``:

        disables the requiretty directive in the sudoers file. this is important if you plan on
        running tasks that require sudo permissions.
        defaults to False.

    ``relocated``:

        set this option to true if the virtualenv that will run this worker has been
        relocated from a different machine. this will make the agent auto-configure the shabang of
        every script in the 'bin' directory of the virtualenv to the proper runtime paths.
        defaults to False.

    :param process_management: The process management to use. Available options: init.d
    :type process_management: str

    :param params: key-value parameters for the daemon.
    :type params: dict

    :return The daemon name.
    :rtype `str`
    """

    daemon = DaemonFactory.new(
        process_management=process_management,
        **params
    )
    daemon.create()
    DaemonFactory.save(daemon)
    return daemon.name


def start(name,
          interval=defaults.START_INTERVAL,
          timeout=defaults.START_TIMEOUT):

    """
    Start the daemon process.

    :param name: The name given to the daemon on `create`.
    :type name: str

    :param interval:
        The interval in seconds to sleep when waiting
        for the daemon to be ready.
    :type interval: int

    :param timeout:
        The timeout in seconds to wait for
        the daemon to be ready.
    :type timeout: int

    """

    daemon = DaemonFactory.load(name)
    daemon.start(
        interval=interval,
        timeout=timeout
    )


def stop(name,
         interval=defaults.STOP_INTERVAL,
         timeout=defaults.STOP_TIMEOUT):

    """
    Stops the daemon process.

    :param name: The name given to the daemon on `create`.
    :type name: str

    :param interval:
        The interval in seconds to sleep when waiting
        for the daemon to stop.
    :type interval: int

    :param timeout:
        The timeout in seconds to wait for
        the daemon to stop.
    :type timeout: int

    """

    daemon = DaemonFactory.load(name)
    daemon.stop(
        interval=interval,
        timeout=timeout
    )


def delete(name):

    """
    Deletes all daemon related files.

    :param name: The name given to the daemon on `create`.
    :type name: str
    """

    daemon = DaemonFactory.load(name)
    daemon.delete()
    DaemonFactory.delete(name)


def register(name, plugin):

    """
    Registers an additional plugin with the daemon. You must
    restart the daemon in order for these changes to take affect.

    :param name: The name given to the daemon on `create`.
    :type name: str

    :param plugin: The plugin name to register.
    :type plugin: str
    """

    daemon = DaemonFactory.load(name)
    daemon.register(plugin)


def restart(name):

    """
    Restarts the daemon process.

    :param name: The name given to the daemon on `create`.
    :type name: str
    """

    daemon = DaemonFactory.load(name)
    daemon.restart()
