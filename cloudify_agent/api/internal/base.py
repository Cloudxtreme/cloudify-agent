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

import os
import logging
import json
import tempfile
import sys

from cloudify.utils import setup_default_logger
from cloudify.utils import LocalCommandRunner

from cloudify_agent.api.internal import DAEMON_CONTEXT_DIR
from cloudify_agent.api import defaults

LOGGER_NAME = 'cloudify.agent.api.daemon'
VIRTUALENV = os.path.dirname(os.path.dirname(sys.executable))

logger = setup_default_logger(LOGGER_NAME,
                              level=logging.INFO)


class DaemonFactory(object):

    @staticmethod
    def _find_implementation(process_management):
        daemons = Daemon.__subclasses__()
        for daemon in daemons:
            if daemon.PROCESS_MANAGEMENT == process_management:
                return daemon
        raise RuntimeError('No implementation found for daemon of type: {0}'
                           .format(process_management))

    @staticmethod
    def create(process_management,
               name,
               queue,
               manager_ip,
               agent_ip,
               user,
               **optional_parameters):
        daemon = DaemonFactory._find_implementation(process_management)
        return daemon(
            name=name,
            queue=queue,
            manager_ip=manager_ip,
            agent_ip=agent_ip,
            user=user,
            **optional_parameters
        )

    @staticmethod
    def load(name):
        daemon_path = os.path.join(
            DAEMON_CONTEXT_DIR,
            '{0}.json'.format(name)
        )
        if not os.path.exists(daemon_path):
            raise IOError('Cannot load daemon: {0} does not exists.'
                          .format(daemon_path))
        runner = LocalCommandRunner(logger=logger)
        contents = runner.run(
            'sudo cat {0}'
            .format(daemon_path)
        ).std_out
        daemon_as_json = json.loads(contents)
        process_management = daemon_as_json.pop('process_management')
        daemon = DaemonFactory._find_implementation(process_management)
        return daemon(
            **daemon_as_json
        )

    @staticmethod
    def save(daemon):
        runner = LocalCommandRunner(logger=logger)
        daemon_path = os.path.join(
            DAEMON_CONTEXT_DIR, '{0}.json'.format(daemon.name)
        )
        temp = tempfile.mkstemp()
        with open(temp[1], 'w') as f:
            props = {
                'name': daemon.name,
                'queue': daemon.queue,
                'manager_ip': daemon.manager_ip,
                'agent_ip': daemon.agent_ip,
                'user': daemon.user,
                'process_management': daemon.PROCESS_MANAGEMENT
            }
            props.update(**daemon.optional_parameters)
            json.dump(props, f, indent=2)
        runner.run(
            'sudo cp {0} {1}'
            .format(temp[1], daemon_path)
        )

    @staticmethod
    def delete(daemon):
        daemon_context = os.path.join(DAEMON_CONTEXT_DIR,
                                      '{0}.json'.format(daemon.name))
        runner = LocalCommandRunner(logger=logger)
        runner.run('sudo rm {0}'.format(daemon_context))


class Daemon(object):

    """
    Base class for all daemon implementations.
    """

    # override this when extending with
    # your own implementation
    PROCESS_MANAGEMENT = None

    def __init__(self,
                 name,
                 queue,
                 agent_ip,
                 manager_ip,
                 user,
                 **optional_parameters):

        # Mandatory arguments
        self.name = name
        self.queue = queue
        self.agent_ip = agent_ip
        self.manager_ip = manager_ip
        self.user = user

        # optional parameters with defaults
        self.broker_ip = optional_parameters.get('broker_ip') or manager_ip
        self.broker_port = optional_parameters.get(
            'broker_port') or defaults.BROKER_PORT
        self.manager_port = optional_parameters.get(
            'manager_port') or defaults.MANAGER_PORT
        self.autoscale = optional_parameters.get(
            'autoscale') or defaults.AUTOSCALE
        self.disable_requiretty = optional_parameters.get(
            'disable_requiretty') or defaults.DISABLE_REQUIRETTY
        self.workdir = optional_parameters.get('workdir') or os.getcwd()

        # configure logger
        self.logger = logger

        self.logger.debug('Working directory for {0} will be: {1}'
                          .format(self.name, self.workdir))

        # save for future reference
        self.optional_parameters = optional_parameters
        self.virtualenv = VIRTUALENV

    def create(self):
        raise NotImplementedError('Must be implemented by subclass')

    def start(self, interval, timeout):
        raise NotImplementedError('Must be implemented by subclass')

    def register(self, plugin):
        raise NotImplementedError('Must be implemented by subclass')

    def stop(self, interval, timeout):
        raise NotImplementedError('Must be implemented by subclass')

    def delete(self):
        raise NotImplementedError('Must be implemented by subclass')

    def restart(self):
        raise NotImplementedError('Must be implemented by subclass')
