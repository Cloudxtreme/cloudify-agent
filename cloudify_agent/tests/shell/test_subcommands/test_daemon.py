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
from click.testing import CliRunner

from cloudify_agent.api import daemon
from cloudify_agent.tests.shell import BaseCommandLineTestCase


class TestGenericLinuxDaemon(BaseCommandLineTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestGenericLinuxDaemon, cls).setUpClass()
        cls.temp_folder = tempfile.mkdtemp(prefix='cloudify-agent-cli-tests-')
        cls.runner = CliRunner()

    def test_create(self):
        self.assert_method_called(
            'cloudify-agent daemon create --queue=queue --agent-ip=127.0.0.1 --manager-ip=127.0.0.1 --user=elip',
            module=daemon,
            function_name='create',
            kwargs={
                'queue': 'queue',
                'agent_ip': '127.0.0.1',
                'manager_ip': '127.0.0.1',
                'user': 'elip',
                'basedir': None,
                'broker_ip': None,
                'broker_port': None,
                'manager_port': None,
                'autoscale': None

            }
        )

    def test_create_optional_parameters(self):
        self.fail()

    def test_register(self):
        self.fail()
