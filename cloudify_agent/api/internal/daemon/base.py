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
from cloudify.utils import LocalCommandRunner

from cloudify_agent.api import defaults
from cloudify_agent.api import daemon_logger
from cloudify_agent import VIRTUALENV


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
                 host,
                 manager_ip,
                 user,
                 **optional_parameters):

        # Mandatory arguments
        self.name = name
        self.queue = queue
        self.host = host
        self.manager_ip = manager_ip
        self.user = user

        # optional parameters with defaults
        self.broker_ip = optional_parameters.get(
            'broker_ip') or manager_ip
        self.broker_port = optional_parameters.get(
            'broker_port') or defaults.BROKER_PORT
        self.manager_port = optional_parameters.get(
            'manager_port') or defaults.MANAGER_PORT
        self.min_workers = optional_parameters.get(
            'min_workers') or defaults.MIN_WORKERS
        self.max_workers = optional_parameters.get(
            'max_workers') or defaults.MAX_WORKERS
        self.disable_requiretty = optional_parameters.get(
            'disable_requiretty') or defaults.DISABLE_REQUIRETTY
        self.workdir = optional_parameters.get(
            'workdir') or os.getcwd()
        self.broker_url = optional_parameters.get(
            'broker_url') or defaults.BROKER_URL.format(
            self.broker_ip,
            self.broker_port)
        self.relocated = optional_parameters.get(
            'relocated') or defaults.RELOCATED

        # configure logger
        self.logger = daemon_logger

        # configure command runner
        self.runner = LocalCommandRunner(logger=self.logger)

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
