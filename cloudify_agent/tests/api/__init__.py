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

from cloudify.celery import celery

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


class BaseApiTestCase(BaseTestCase):

    def setUp(self):
        super(BaseApiTestCase, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(BaseApiTestCase, cls).setUpClass()

    def assertRegisteredTasks(self, queue, additional_tasks=None):
        # assert tasks are registered as we expect
        if not additional_tasks:
            additional_tasks = set()
        destination = 'celery.{0}'.format(queue)
        inspect = celery.control.inspect(destination=[destination])
        registered = inspect.registered() or {}

        def include(task):
            return 'celery' not in task

        daemon_tasks = set(filter(include, set(registered[destination])))
        expected_tasks = set(BUILT_IN_TASKS)
        expected_tasks.update(additional_tasks)
        self.assertEqual(expected_tasks, daemon_tasks)
