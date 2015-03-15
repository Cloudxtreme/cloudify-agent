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

import uuid
import os
from celery import Celery

from cloudify.utils import LocalCommandRunner
from cloudify.utils import setup_default_logger

from cloudify_agent.api import defaults
from cloudify_agent.api import errors


MANDATORY_PARAMS = [
    'manager_ip',
    'user'
]


class Daemon(object):

    """
    Base class for daemon implementations.
    Following is all the common daemon keyword arguments:

    ``name``:

        the name to give the agent. This name will be a unique identifier of
        the daemon. meaning you will not be able to create more agents with
        that name until a delete operation has been performed.

    ``queue``:

        the queue this agent will listen to. It is possible to create
        different workers with the same queue, however this is discouraged.
        to create more workers that process tasks
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
        broker_ip and broker_port like so:
        'amqp://guest:guest@<broker_ip>:<broker_port>//'

    ``manager_port``:

        the manager REST gateway port to connect to. defaults to 80.

    ``min_workers``:

        the minimum number of worker processes this agent will manage. all
        workers will listen on the same queue allowing for higher
        concurrency when preforming tasks. defaults to 0.

    ``max_workers``:

        the maximum number of worker processes this agent will manager.
        as tasks keep coming in, the agent will expand its worker pool to
        handle more tasks concurrently. However, as the name
        suggests, it will never exceed this number. allowing for the control
        of resource usage. defaults to 5.

    """

    # override this when adding implementations.
    PROCESS_MANAGEMENT = None

    def __init__(self, **params):

        # Mandatory parameters
        self.validate_mandatory(params)

        self.manager_ip = params['manager_ip']
        self.user = params['user']

        # Optional parameters
        self.validate_optional(params)

        broker_ip = params.get(
            'broker_ip') or self.manager_ip
        broker_port = params.get(
            'broker_port') or defaults.BROKER_PORT

        self.name = params.get(
            'name') or 'cloudify-agent-{0}'.format(uuid.uuid4())
        self.queue = params.get(
            'queue') or '{0}-queue'.format(self.name)
        self.host = params.get(
            'host') or '127.0.0.1'
        self.broker_url = params.get(
            'broker_url') or defaults.BROKER_URL.format(
            broker_ip,
            broker_port)
        self.manager_port = params.get(
            'manager_port') or defaults.MANAGER_PORT
        self.min_workers = params.get(
            'min_workers') or defaults.MIN_WORKERS
        self.max_workers = params.get(
            'max_workers') or defaults.MAX_WORKERS
        self.workdir = params.get(
            'workdir') or os.getcwd()

        # save as a property so that it will be persisted in the json files
        self.process_management = self.PROCESS_MANAGEMENT

        # configure logger
        self.logger = setup_default_logger(
            'cloudify_agent.api.pm.{0}'
            .format(self.PROCESS_MANAGEMENT))

        # configure command runner
        self.runner = LocalCommandRunner(logger=self.logger)

        # initialize an internal celery client
        self.celery = Celery(broker=self.broker_url,
                             backend=self.broker_url)

    @staticmethod
    def validate_mandatory(params):

        """
        Validates that all mandatory parameters are given.

        :param params: parameters of the daemon.
        :type params: dict

        :raise MissingMandatoryParamError:
        in case one of the mandatory parameters is missing.
        """

        for param in MANDATORY_PARAMS:
            value = params.get(param)
            if not value:
                raise errors.MissingMandatoryParamError(param)

    @staticmethod
    def validate_optional(params):

        """
        Validates any optional parameters given to the daemon.

        :param params: parameters of the daemon.
        :type params: dict

        :raise DaemonConfigurationError:
        in case one of the parameters is faulty.
        """

        min_workers = params.get('min_workers')
        max_workers = params.get('max_workers')

        if min_workers:
            if not str(min_workers).isdigit():
                raise errors.DaemonParametersError(
                    'min_workers is supposed to be a number '
                    'but is: {0}'
                    .format(min_workers)
                )
            min_workers = int(min_workers)

        if max_workers:
            if not str(max_workers).isdigit():
                raise errors.DaemonParametersError(
                    'max_workers is supposed to be a number '
                    'but is: {0}'
                    .format(max_workers)
                )
            max_workers = int(max_workers)

        if min_workers and max_workers:
            if min_workers > max_workers:
                raise errors.DaemonParametersError(
                    'min_workers cannot be greater than max_workers '
                    '[min_workers={0}, max_workers={1}]'
                    .format(min_workers, max_workers))

    def create(self):

        """
        Creates any necessary resources for the daemon. This method MUST be
        able to execute without sudo permissions.
        """
        raise NotImplementedError('Must be implemented by subclass')

    def configure(self):

        """
        Configures the daemon. This method must create all necessary
        configuration of the daemon.

        :return: The daemon name.
        :rtype `str`
        """
        raise NotImplementedError('Must be implemented by subclass')

    def start(self, interval, timeout):

        """
        Starts the daemon process.

        :param interval: the interval in seconds to sleep when waiting for
        the daemon to be ready.
        :type interval: int

        :param timeout: the timeout in seconds to wait for the daemon to be
        ready.
        :type timeout: int
        """
        raise NotImplementedError('Must be implemented by subclass')

    def register(self, plugin):

        """
        Register an additional plugin. This method must enable the addition
        of operations defined in the plugin.

        :param plugin: The plugin name to register.
        :type plugin: str
        """
        raise NotImplementedError('Must be implemented by subclass')

    def stop(self, interval, timeout):

        """
        Stops the daemon process.

        :param interval: the interval in seconds to sleep when waiting for
        the daemon to stop.
        :type interval: int

        :param timeout: the timeout in seconds to wait for the daemon to stop.
        :type timeout: int
        """
        raise NotImplementedError('Must be implemented by subclass')

    def delete(self):

        """
        Delete any resources created by the daemon.

        """
        raise NotImplementedError('Must be implemented by subclass')

    def restart(self,
                start_timeout=defaults.START_TIMEOUT,
                start_interval=defaults.START_INTERVAL,
                stop_timeout=defaults.STOP_TIMEOUT,
                stop_interval=defaults.STOP_INTERVAL):

        """
        Restart the daemon process.

        :param start_interval: the interval in seconds to sleep when waiting
        for the daemon to start.
        :type start_interval: int

        :param start_timeout: The timeout in seconds to wait for the daemon
        to start.
        :type start_timeout: int

        :param stop_interval: the interval in seconds to sleep when waiting
        for the daemon to stop.
        :type stop_interval: int

        :param stop_timeout: the timeout in seconds to wait for the daemon
        to stop.
        :type stop_timeout: int

        """
        raise NotImplementedError('Must be implemented by subclass')