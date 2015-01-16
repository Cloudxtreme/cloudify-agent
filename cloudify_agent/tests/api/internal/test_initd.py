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

from cloudify.utils import LocalCommandRunner

from cloudify_agent.api.internal.initd import GenericLinuxDaemon
from cloudify_agent.tests.api import BaseApiTestCase

from cloudify_agent.tests import resources


class TestGenericLinuxDaemon(BaseApiTestCase):

    PROCESS_MANAGEMENT = 'init.d'

    @classmethod
    def setUpClass(cls):
        super(TestGenericLinuxDaemon, cls).setUpClass()
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
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        self.assertTrue(os.path.exists(daemon.script_path))
        self.assertTrue(os.path.exists(daemon.config_path))

    def test_delete(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        daemon.start()
        daemon.stop()
        daemon.delete()
        self.assertFalse(os.path.exists(daemon.script_path))
        self.assertFalse(os.path.exists(daemon.config_path))

    def test_start(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        daemon.start()
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)

    def test_stop(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        daemon.start()
        daemon.stop()
        self.assert_daemon_dead(self.queue)

    def test_register(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
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

    def test_restart(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        from cloudify_agent.tests import resources
        self.runner.run('{0}/bin/pip install {1}/mock-plugin'
                        .format(daemon.virtualenv,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        daemon.start()
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

    def test_create_twice(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        self.assertRaises(RuntimeError, daemon.create)

    def test_create_twice_only_script_path_exists(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()

        # delete includes and config files
        runner = LocalCommandRunner(self.logger)
        runner.run('sudo rm {0}'.format(daemon.includes_file_path))
        runner.run('sudo rm {0}'.format(daemon.config_path))

        self.assertRaises(RuntimeError, daemon.create)

    def test_create_twice_only_config_path_exists(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()

        # delete includes and script files
        self.runner.run('sudo rm {0}'.format(daemon.includes_file_path))
        self.runner.run('sudo rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon.create)

    def test_create_twice_only_includes_path_exists(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()

        # delete config and script files
        self.runner.run('sudo rm {0}'.format(daemon.config_path))
        self.runner.run('sudo rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon.create)

    def test_start_with_error(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        self.runner.run('{0}/bin/pip install {1}/mock-plugin-error'
                        .format(daemon.virtualenv,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        try:
            daemon.register('mock-plugin-error')
            try:
                daemon.start()
                self.fail('Expected start operation to fail '
                          'due to bad import')
            except RuntimeError as e:
                self.assertIn('cannot import name non_existent', str(e))
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin-error'
                            .format(daemon.virtualenv),
                            stdout_pipe=False)

    def test_start_short_timeout(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        try:
            daemon.start(timeout=-1)
        except RuntimeError as e:
            self.assertIn('waited for -1 seconds', str(e))

    def test_start_twice(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        daemon.start()
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)
        daemon.start()
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)

    def test_stop_short_timeout(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        daemon.start()
        try:
            daemon.stop(timeout=-1)
        except RuntimeError as e:
            self.assertIn('waited for -1 seconds', str(e))

    def test_stop_twice(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        daemon.start()
        daemon.stop()
        self.assert_daemon_dead(self.queue)
        daemon.stop()
        self.assert_daemon_dead(self.queue)

    def test_two_daemons(self):
        queue1 = '{0}-1'.format(self.queue)
        name1 = '{0}-1'.format(self.name)
        daemon1 = GenericLinuxDaemon(
            name=name1,
            queue=queue1,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon1.create()

        daemon1.start()
        self.assert_daemon_alive(queue1)
        self.assert_registered_tasks(queue1)

        queue2 = '{0}-2'.format(self.queue)
        name2 = '{0}-2'.format(self.name)
        daemon2 = GenericLinuxDaemon(
            name=name2,
            queue=queue2,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon2.create()

        daemon2.start()
        self.assert_daemon_alive(queue2)
        self.assert_registered_tasks(queue2)

    def test_delete_before_stop(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.create()
        daemon.start()
        self.assertRaises(RuntimeError, daemon.delete)
