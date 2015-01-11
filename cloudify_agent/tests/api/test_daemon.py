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

import os
from cloudify_agent.api.internal import DAEMON_CONTEXT_DIR

from cloudify_agent.tests.api import BaseApiTestCase
from cloudify_agent.api import daemon as api


class TestApi(BaseApiTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestApi, cls).setUpClass()
        if 'TRAVIS_BUILD_DIR' not in os.environ \
                and 'FORCE_TESTS' not in os.environ:
            raise RuntimeError(
                'Error! These tests require sudo '
                'permissions and may manipulate system wide files. '
                'Therefore they are only executed on the travis CI system. '
                'If you are ABSOLUTELY sure you wish to '
                'run them on your local box, set the FORCE_TESTS '
                'environment variable to bypass this restriction.')

    def test_create(self):
        api.create(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='init.d'
        )
        daemon_context = os.path.join(DAEMON_CONTEXT_DIR,
                                      '{0}.json'.format(self.name))
        self.assertTrue(os.path.exists(os.path.join(daemon_context)))

    def test_start(self):
        api.create(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='init.d'
        )
        api.start(self.name)
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(self.queue)

    def test_stop(self):
        api.create(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='init.d'
        )
        api.start(self.name)
        api.stop(self.name)
        self.assert_daemon_dead(self.queue)

    def test_register(self):
        from cloudify_agent.tests import resources
        daemon = api.create(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='init.d'
        )
        self.runner.run('{0}/bin/pip install {1}/mock-plugin'
                        .format(daemon.virtualenv,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        try:
            daemon.register('mock-plugin')
            daemon.start()
            self.assert_registered_tasks(
                self.queue,
                additional_tasks=set(['mock_plugin.tasks.run'])
            )
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin'
                            .format(daemon.virtualenv),
                            stdout_pipe=False)

    def test_delete(self):
        api.create(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='init.d'
        )
        api.start(self.name)
        api.stop(self.name)
        api.delete(self.name)
        daemon_context = os.path.join(DAEMON_CONTEXT_DIR,
                                      '{0}.json'.format(self.name))
        self.assertFalse(os.path.exists(os.path.join(daemon_context)))

    def test_restart(self):
        from cloudify_agent.tests import resources
        daemon = api.create(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='init.d'
        )
        self.runner.run('{0}/bin/pip install {1}/mock-plugin'
                        .format(daemon.virtualenv,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        api.start(self.name)
        self.assert_registered_tasks(self.queue)
        try:
            daemon.register('mock-plugin')
            daemon.restart()
            self.assert_registered_tasks(
                self.queue,
                additional_tasks=set(['mock_plugin.tasks.run'])
            )
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin'
                            .format(daemon.virtualenv),
                            stdout_pipe=False)
