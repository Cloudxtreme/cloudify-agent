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
from celery import Celery

from cloudify_agent.api import defaults
from cloudify_agent.api import daemon_logger


MANDATORY_PARAMS = [
    'name',
    'queue',
    'host',
    'manager_ip',
    'user'
]


class Daemon(object):

    """
    Base class for all daemon implementations.
    """

    # override this when adding implementations.
    PROCESS_MANAGEMENT = None

    def __init__(self, **params):

        # Mandatory parameters
        self._validate_mandatory(params)

        self.name = params['name']
        self.queue = params['queue']
        self.host = params['host']
        self.manager_ip = params['manager_ip']
        self.user = params['user']

        # Optional parameters
        self._validate_optional(params)

        broker_ip = params.get(
            'broker_ip') or self.manager_ip
        broker_port = params.get(
            'broker_port') or defaults.BROKER_PORT

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
        self.disable_requiretty = params.get(
            'disable_requiretty') or defaults.DISABLE_REQUIRETTY
        self.workdir = params.get(
            'workdir') or os.getcwd()
        self.relocated = params.get(
            'relocated') or defaults.RELOCATED

        self.process_management = self.PROCESS_MANAGEMENT

        # configure logger
        self.logger = daemon_logger

        # configure command runner
        self.runner = LocalCommandRunner(logger=self.logger)

        # initialize an internal celery client
        self.celery = Celery(broker=self.broker_url,
                             backend=self.broker_url)

    @staticmethod
    def _validate_mandatory(params):

        """
        Validates all mandatory parameters are given.

        :param params: parameters of the daemon.
        :type params: dict

        :raise ValueError: in case one of the mandatory parameters is missing.
        """

        for param in MANDATORY_PARAMS:
            value = params.get(param)
            if not value:
                raise ValueError(
                    '{0} is mandatory'
                    .format(param)
                )

    @staticmethod
    def _validate_optional(params):

        """
        Validates any optional parameters given to the daemon.

        :param params: parameters of the daemon.
        :type params: dict

        :raise ValueError: in case one of the parameters is faulty.
        """

        min_workers = params.get('min_workers')
        max_workers = params.get('max_workers')

        if min_workers:
            if not str(min_workers).isdigit():
                raise ValueError('min_workers is supposed to be a number '
                                 'but is: {0}'.format(min_workers))
            min_workers = int(min_workers)

        if max_workers:
            if not str(max_workers).isdigit():
                raise ValueError('max_workers is supposed to be a number '
                                 'but is: {0}'.format(max_workers))
            max_workers = int(max_workers)

        if min_workers and max_workers:
            if min_workers > max_workers:
                raise ValueError(
                    'min_workers cannot be greater than max_workers '
                    '[min_workers={0}, max_workers={1}]'
                    .format(min_workers, max_workers))

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
