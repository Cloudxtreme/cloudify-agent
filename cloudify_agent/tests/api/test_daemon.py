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
import logging
import getpass
import os

from cloudify.utils import LocalCommandRunner
from cloudify.celery import celery

from cloudify_agent.api.daemon import Daemon
from cloudify_agent.api import daemon as daemon_api
from cloudify_agent.tests.api import BaseApiTestCase


username = getpass.getuser()


class TestDaemonDefaults(BaseApiTestCase):

    """
    Tests the fallback behavior of all optional
    initialization parameters.
    """

    def setUp(self):
        super(TestDaemonDefaults, self).setUp()
        self.daemon = Daemon(
            queue='test_queue'
        )

    def test_default_basedir(self):
        self.assertEqual(os.getcwd(), self.daemon.workdir)

    def test_default_broker_port(self):
        self.assertEqual(5672, self.daemon.broker_port)

    def test_default_manager_port(self):
        self.assertEqual(80, self.daemon.manager_port)

    def test_default_autoscale(self):
        self.assertEqual('0,5', self.daemon.autoscale)


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

    def setUp(self):
        super(TestGenericLinuxDaemon, self).setUp()
        self.queue = 'test_queue-{0}'.format(str(uuid.uuid4())[0:4])
        self.runner = LocalCommandRunner(self.logger)
        logging.getLogger('cloudify.agent.api.daemon').setLevel(logging.DEBUG)

    def tearDown(self):
        super(TestGenericLinuxDaemon, self).tearDown()
        pong = celery.control.ping()
        if pong:
            self.runner.run("pkill -9 -f 'celery.bin.celeryd'")

    def test_create(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        self.assertTrue(os.path.exists(daemon.script_path))
        self.assertTrue(os.path.exists(daemon.config_path))

    def test_create_twice(self):
        daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        self.assertRaises(RuntimeError, daemon_api.create,
                          queue=self.queue,
                          agent_ip='127.0.0.1',
                          manager_ip='127.0.0.1',
                          user=self.username,
                          process_management=self.PROCESS_MANAGEMENT,
                          basedir=self.temp_folder)

    def test_create_twice_only_script_path_exists(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        # delete includes and config files
        runner = LocalCommandRunner(self.logger)
        runner.run('sudo rm {0}'.format(daemon.includes_file_path))
        runner.run('sudo rm {0}'.format(daemon.config_path))

        self.assertRaises(RuntimeError, daemon_api.create,
                          queue=self.queue,
                          agent_ip='127.0.0.1',
                          manager_ip='127.0.0.1',
                          user=self.username,
                          process_management=self.PROCESS_MANAGEMENT,
                          basedir=self.temp_folder)

    def test_create_twice_only_config_path_exists(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        # delete includes and script files
        self.runner.run('sudo rm {0}'.format(daemon.includes_file_path))
        self.runner.run('sudo rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon_api.create,
                          queue=self.queue,
                          agent_ip='127.0.0.1',
                          manager_ip='127.0.0.1',
                          user=self.username,
                          process_management=self.PROCESS_MANAGEMENT,
                          basedir=self.temp_folder)

    def test_create_twice_only_includes_path_exists(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        # delete config and script files
        self.runner.run('sudo rm {0}'.format(daemon.config_path))
        self.runner.run('sudo rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon_api.create,
                          queue=self.queue,
                          agent_ip='127.0.0.1',
                          manager_ip='127.0.0.1',
                          user=self.username,
                          process_management=self.PROCESS_MANAGEMENT,
                          basedir=self.temp_folder)

    def test_start(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        daemon_api.start(self.queue)
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)

    def test_start_twice(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        daemon_api.start(self.queue)
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)
        daemon_api.start(self.queue)
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)

    def test_stop(self):
        daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        daemon_api.start(self.queue)
        daemon_api.stop(self.queue)
        self.assert_daemon_dead(self.queue)

    def test_stop_twice(self):
        daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        daemon_api.start(self.queue)
        daemon_api.stop(self.queue)
        self.assert_daemon_dead(self.queue)
        daemon_api.stop(self.queue)
        self.assert_daemon_dead(self.queue)

    def test_register_before_start(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        from cloudify_agent.tests import resources
        self.runner.run('{0}/bin/pip install {1}/mock-plugin'
                        .format(daemon.virtualenv_path,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        try:
            daemon_api.register(self.queue, 'mock-plugin')
            daemon_api.start(self.queue)
            self.assert_registered_tasks(
                self.queue,
                additional_tasks=set(['mock_plugin.tasks.run'])
            )
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin'
                            .format(daemon.virtualenv_path),
                            stdout_pipe=False)

    def test_register_after_started(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        from cloudify_agent.tests import resources
        self.runner.run('{0}/bin/pip install {1}/mock-plugin'
                        .format(daemon.virtualenv_path,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        daemon_api.start(self.queue)
        try:
            daemon_api.register(self.queue, 'mock-plugin')
            daemon_api.restart(self.queue)
            self.assert_registered_tasks(
                self.queue,
                additional_tasks=set(['mock_plugin.tasks.run'])
            )
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin'
                            .format(daemon.virtualenv_path),
                            stdout_pipe=False)

    def test_two_daemons(self):
        queue1 = '{0}-1'.format(self.queue)
        daemon_api.create(
            queue=queue1,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        daemon_api.start(queue1)
        self.assert_daemon_alive(queue1)
        self.assert_registered_tasks(queue1)

        queue2 = '{0}-2'.format(self.queue)
        daemon_api.create(
            queue=queue2,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        daemon_api.start(queue2)
        self.assert_daemon_alive(queue2)
        self.assert_registered_tasks(queue2)

    def test_delete_before_stop(self):
        daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        daemon_api.start(self.queue)
        self.assertRaises(RuntimeError, daemon_api.delete)

    def test_delete_after_stop(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )
        daemon_api.start(self.queue)
        daemon_api.stop(self.queue)
        daemon_api.delete(self.queue)
        self.assertFalse(os.path.exists(daemon.script_path))
        self.assertFalse(os.path.exists(daemon.config_path))
