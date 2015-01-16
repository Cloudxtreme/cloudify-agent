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

from cloudify_agent.api.internal.base import DaemonFactory


"""
Public API for controlling a Daemon's lifecycle.
"""


def create(name,
           queue,
           agent_ip,
           manager_ip,
           user,
           process_management,
           **optional_parameters):

    """
    Creates the necessary scripts and configuration files for the daemon.
    This operation also saves the daemon to a file, allowing subsequent
    calls to load the daemon by using `DaemonFactory.load(daemon_name)`.

    :param name: The daemon name. Must be unique.
    :param queue: The queue this daemon will listen to.
    :param agent_ip: A resolvable IP address of the daemon host.
    :param manager_ip: A resolvable IP address of the manager machine.
    :param user: The user under which this daemon will be created.
    :param process_management: The process management to use.
    :param optional_parameters: A dictionary containing any additional,
                                non mandatory parameters.
    :return: The daemon instance.
    :rtype: `cloudify_agent.api.daemons.Daemon`
    """

    daemon = DaemonFactory.create(
        process_management=process_management,
        name=name,
        queue=queue,
        manager_ip=manager_ip,
        agent_ip=agent_ip,
        user=user,
        **optional_parameters
    )
    daemon.create()
    DaemonFactory.save(daemon)
    return daemon


def start(name, interval, timeout):

    """
    Start the daemon process.

    :param name: The name given to the daemon on `create`.

    :param interval:
        The interval in seconds to sleep when waiting
        for the daemon to be ready

    :param timeout:
        The timeout in seconds to wait for
        the daemon to be ready.

    :return: The daemon instance.
    :rtype: `cloudify_agent.api.daemons.Daemon`
    """

    daemon = DaemonFactory.load(name)
    daemon.start(
        interval=interval,
        timeout=timeout
    )
    return daemon


def stop(name, interval, timeout):

    """
    Stops the daemon process.

    :param name: The name given to the daemon on `create`.

    :param interval:
        The interval in seconds to sleep when waiting
        for the daemon to stop.

    :param timeout:
        The timeout in seconds to wait for
        the daemon to stop.

    :return: The daemon instance.
    :rtype: `cloudify_agent.api.daemons.Daemon`
    """

    daemon = DaemonFactory.load(name)
    daemon.stop(
        interval=interval,
        timeout=timeout
    )
    return daemon


def delete(name):

    """
    Deletes all daemon related files.

    :param name: The name given to the daemon on `create`.
    :return: The daemon instance.
    :rtype: `cloudify_agent.api.daemons.Daemon`
    """

    daemon = DaemonFactory.load(name)
    daemon.delete()
    DaemonFactory.delete(daemon)
    return daemon


def register(name, plugin):

    """
    Registers an additional plugin with the daemon. You must
    restart the daemon in order for these changes to take affect.

    :param name: The name given to the daemon on `create`.
    :return: The daemon instance.
    :rtype: `cloudify_agent.api.daemons.Daemon`
    """

    daemon = DaemonFactory.load(name)
    daemon.register(plugin)
    return daemon


def restart(name):

    """
    Restarts the daemon process.

    :param name: The name given to the daemon on `create`.
    :return: The daemon instance.
    :rtype: `cloudify_agent.api.daemons.Daemon`
    """

    daemon = DaemonFactory.load(name)
    daemon.restart()
    return daemon
