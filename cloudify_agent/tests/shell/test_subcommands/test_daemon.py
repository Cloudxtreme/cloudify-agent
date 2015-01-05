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
import tempfile
from click.testing import CliRunner

from cloudify_agent.shell.subcommands.daemon import create
from cloudify_agent.tests import BaseTestCase


class TestGenericLinuxDaemon(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_folder = tempfile.mkdtemp(prefix='cloudify-agent-tests-')
        cls.runner = CliRunner()

    def test_create(self):
        queue = 'test_queue-{0}'.format(str(uuid.uuid4())[0:4])
        expected_message = 'Successfully created {0} daemon'.format(
            'celeryd-{0}'.format(queue)
        )
        result = self.runner.invoke(create, [
            '--queue={0}'.format(queue),
            '--ip=127.0.0.1',
            '--manager_ip=127.0.0.1',
            '--user=elip',
            '--basedir={0}'.format(self.temp_folder)
        ])
        self.assertRegisteredTasks(queue)
        self.assertIn(expected_message, result.output)

    def test_create_optional_parameters(self):
        self.fail()

    def test_register(self):
        self.fail()
