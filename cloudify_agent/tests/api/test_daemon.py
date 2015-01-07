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

from cloudify_agent.api.daemon import Daemon
from cloudify_agent.api import daemon as daemon_api
from cloudify.utils import LocalCommandRunner

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
                'If you are ABSOLUTELY sure you wish to run them on your local box, '
                'set the FORCE_TESTS environment variable to bypass this restriction.')

    def setUp(self):
        super(TestGenericLinuxDaemon, self).setUp()
        self.queue = 'test_queue-{0}'.format(str(uuid.uuid4())[0:4])
        self.runner = LocalCommandRunner(self.logger)
        self.daemon_names = []
        logging.getLogger('cloudify.agent.api.daemon').setLevel(logging.DEBUG)

    def tearDown(self):
        super(TestGenericLinuxDaemon, self).tearDown()
        if self.daemon_names:
            for daemon_name in self.daemon_names:
                self.runner.run('sudo service {0} stop'
                                .format(daemon_name))

    def test_create(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        self.runner.run('sudo service {0} start'.format(daemon.name))
        self.daemon_names.append(daemon.name)
        self.assertRegisteredTasks(self.queue)

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

    def test_two_daemons(self):
        queue1 = '{0}-1'.format(self.queue)
        daemon = daemon_api.create(
            queue=queue1,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        self.runner.run('sudo service {0} start'.format(daemon.name))
        self.daemon_names.append(daemon.name)
        self.assertRegisteredTasks(queue1)

        queue2 = '{0}-2'.format(self.queue)
        daemon = daemon_api.create(
            queue=queue2,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            process_management=self.PROCESS_MANAGEMENT
        )

        self.runner.run('sudo service {0} start'.format(daemon.name))
        self.daemon_names.append(daemon.name)
        self.assertRegisteredTasks(queue2)

    def test_register(self):
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
            self.runner.run('sudo service {0} start'.format(daemon.name))
            self.daemon_name = daemon.name
            self.assertRegisteredTasks(
                self.queue,
                additional_tasks=set(['mock_plugin.tasks.run'])
            )
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin'
                            .format(daemon.virtualenv_path),
                            stdout_pipe=False)
