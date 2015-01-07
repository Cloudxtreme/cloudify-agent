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

import tempfile
import os
import uuid
import logging

from cloudify_agent.api.daemon import Daemon
from cloudify_agent.api import daemon as daemon_api
from cloudify.utils import LocalCommandRunner

from cloudify_agent.tests.api import BaseApiTestCase


class TestDaemonDefaults(BaseApiTestCase):

    """
    Tests the fallback behavior of all optional
    initialization parameters.
    """

    @classmethod
    def setUpClass(cls):

        cls.daemon = Daemon(
            queue='test_queue'
        )

    def test_default_basedir(self):
        self.assertEqual(os.getcwd(), self.daemon.basedir)

    def test_default_broker_port(self):
        self.assertEqual(5672, self.daemon.broker_port)

    def test_default_manager_port(self):
        self.assertEqual(80, self.daemon.manager_port)

    def test_default_autoscale(self):
        self.assertEqual('0,5', self.daemon.autoscale)


class TestGenericLinuxDaemon(BaseApiTestCase):

    """
    Tests the functionality of the GenericLinuxDaemon.
    """

    def setUp(self):
        super(TestGenericLinuxDaemon, self).setUp()
        self.temp_folder = tempfile.mkdtemp(prefix='cloudify-agent-api-tests-')
        self.queue = 'test_queue-{0}'.format(str(uuid.uuid4())[0:4])
        self.runner = LocalCommandRunner(self.logger)
        self.daemon_name = None
        logging.getLogger('cloudify.agent.api.daemon').setLevel(logging.DEBUG)

    def tearDown(self):
        super(TestGenericLinuxDaemon, self).tearDown()
        if self.daemon_name:
            self.runner.run('sudo service cloudify-agent-{0} stop'
                            .format(self.queue))

    def test_create(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            basedir=self.temp_folder
        )

        self.runner.run('sudo service {0} start'.format(daemon.name))
        self.daemon_name = daemon.name
        self.assertRegisteredTasks(self.queue)

    def test_create_twice(self):
        daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            basedir=self.temp_folder
        )
        self.assertRaises(RuntimeError, daemon_api.create,
                          queue=self.queue,
                          agent_ip='127.0.0.1',
                          manager_ip='127.0.0.1',
                          user=self.username,
                          basedir=self.temp_folder)

    def test_create_twice_only_script_path_exists(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            basedir=self.temp_folder
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
                          basedir=self.temp_folder)

    def test_create_twice_only_config_path_exists(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            basedir=self.temp_folder
        )

        # delete includes and script files
        self.runner.run('sudo rm {0}'.format(daemon.includes_file_path))
        self.runner.run('sudo rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon_api.create,
                          queue=self.queue,
                          agent_ip='127.0.0.1',
                          manager_ip='127.0.0.1',
                          user=self.username,
                          basedir=self.temp_folder)

    def test_create_twice_only_includes_path_exists(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            basedir=self.temp_folder
        )

        # delete config and script files
        self.runner.run('sudo rm {0}'.format(daemon.config_path))
        self.runner.run('sudo rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon_api.create,
                          queue=self.queue,
                          agent_ip='127.0.0.1',
                          manager_ip='127.0.0.1',
                          user=self.username,
                          basedir=self.temp_folder)

    def test_register(self):
        daemon = daemon_api.create(
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            basedir=self.temp_folder
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
