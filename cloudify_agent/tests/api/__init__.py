#########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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
import logging
import shutil
from mock import _get_target
from mock import patch

from celery import Celery
from cloudify.utils import LocalCommandRunner

from cloudify_agent.tests import BaseTestCase


BUILT_IN_TASKS = [
    'script_runner.tasks.execute_workflow',
    'script_runner.tasks.run',
    'diamond_agent.tasks.install',
    'diamond_agent.tasks.uninstall',
    'diamond_agent.tasks.start',
    'diamond_agent.tasks.stop',
    'diamond_agent.tasks.add_collectors',
    'diamond_agent.tasks.del_collectors',
    'worker_installer.tasks.install',
    'worker_installer.tasks.uninstall',
    'worker_installer.tasks.start',
    'worker_installer.tasks.stop',
    'worker_installer.tasks.restart',
    'plugin_installer.tasks.install',
    'windows_agent_installer.tasks.install',
    'windows_agent_installer.tasks.uninstall',
    'windows_agent_installer.tasks.start',
    'windows_agent_installer.tasks.stop',
    'windows_agent_installer.tasks.restart',
    'windows_plugin_installer.tasks.install'
]

CLOUDIFY_STORAGE_FOLDER = '/tmp/var/lib/docker'
SCRIPT_DIR = '/tmp/etc/init.d'
CONFIG_DIR = '/tmp/etc/default'


class SudoLessLocalCommandRunner(LocalCommandRunner):

    """
    Command runner that runs `sudo` exactly the
    same as `run`. (i.e no 'sudo' prefix)

    """

    def sudo(self, command,
             exit_on_failure=True,
             stdout_pipe=True,
             stderr_pipe=True,
             cwd=None):
        return super(SudoLessLocalCommandRunner, self).run(
            command,
            exit_on_failure,
            stdout_pipe,
            stderr_pipe,
            cwd
        )


def travis():
    return 'TRAVIS_BUILD_DIR' in os.environ


def patch_unless_travis(target, new):

    if not travis():
        return patch(target, new)
    else:
        getter, attribute = _get_target(target)
        return patch(target, getattr(getter(), attribute))


class BaseApiTestCase(BaseTestCase):

    def setUp(self):
        super(BaseApiTestCase, self).setUp()
        self.name = 'cloudify-agent-{0}'.format(str(uuid.uuid4())[0:4])
        self.queue = '{0}-queue'.format(self.name)
        if travis():
            # travis CI can run sudo commands
            self.runner = LocalCommandRunner(self.logger)
        else:
            # when running locally, avoid sudo
            self.runner = SudoLessLocalCommandRunner(self.logger)
        self._smakedirs(CLOUDIFY_STORAGE_FOLDER)
        self._smakedirs(CONFIG_DIR)
        self._smakedirs(SCRIPT_DIR)
        logging.getLogger('cloudify-agent.api.daemon').setLevel(logging.DEBUG)
        self.celery = Celery(broker='amqp://',
                             backend='amqp://')

    def tearDown(self):
        super(BaseApiTestCase, self).tearDown()
        self._srmtree(CLOUDIFY_STORAGE_FOLDER)
        self._srmtree(CONFIG_DIR)
        self._srmtree(SCRIPT_DIR)
        pong = self.celery.control.ping()
        if pong:
            self.runner.run("pkill -9 -f 'celery.bin.celeryd'")

    def _smakedirs(self, dirs):
        if not os.path.exists(dirs):
            os.makedirs(dirs)

    def _srmtree(self, tree):
        if os.path.exists(tree):
            shutil.rmtree(tree)

    def assert_registered_tasks(self, queue, additional_tasks=None):
        if not additional_tasks:
            additional_tasks = set()
        destination = 'celery.{0}'.format(queue)
        inspect = self.celery.control.inspect(destination=[destination])
        registered = inspect.registered() or {}

        def include(task):
            return 'celery' not in task

        daemon_tasks = set(filter(include, set(registered[destination])))
        expected_tasks = set(BUILT_IN_TASKS)
        expected_tasks.update(additional_tasks)
        self.assertEqual(expected_tasks, daemon_tasks)

    def assert_daemon_alive(self, queue):
        destination = 'celery.{0}'.format(queue)
        inspect = self.celery.control.inspect(destination=[destination])
        stats = (inspect.stats() or {}).get(destination)
        self.assertIsNotNone(stats)

    def assert_daemon_dead(self, queue):
        destination = 'celery.{0}'.format(queue)
        inspect = self.celery.control.inspect(destination=[destination])
        stats = (inspect.stats() or {}).get(destination)
        self.assertIsNone(stats)
