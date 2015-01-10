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

from cloudify_agent.api import daemon
from cloudify_agent.tests.shell import BaseCommandLineTestCase


class TestDaemonCommandLine(BaseCommandLineTestCase):

    PROCESS_MANAGEMENT = 'init.d'

    def test_create(self):
        self.assert_method_called(
            'cloudify-agent daemon create --name=name --queue=queue --agent-ip=127.0.0.1 '
            '--manager-ip=127.0.0.1 --user={0}'.format(self.username),
            module=daemon,
            function_name='create',
            kwargs={
                'name': 'name',
                'queue': 'queue',
                'agent_ip': '127.0.0.1',
                'manager_ip': '127.0.0.1',
                'user': self.username,
                'process_management': 'init.d',
                'workdir': None,
                'broker_ip': None,
                'broker_port': None,
                'manager_port': None,
                'autoscale': None
            }
        )

    def test_start(self):
        self.assert_method_called(
            'cloudify-agent daemon start --name=name',
            module=daemon,
            function_name='start',
            args=['name']
        )

    def test_stop(self):
        self.assert_method_called(
            'cloudify-agent daemon stop --name=name',
            module=daemon,
            function_name='stop',
            args=['name']
        )

    def test_delete(self):
        self.assert_method_called(
            'cloudify-agent daemon delete --name=name',
            module=daemon,
            function_name='delete',
            args=['name']
        )

    def test_restart(self):
        self.assert_method_called(
            'cloudify-agent daemon restart --name=name',
            module=daemon,
            function_name='restart',
            args=['name']
        )

    def test_register(self):
        self.assert_method_called(
            'cloudify-agent daemon register --name=name --plugin=plugin',
            module=daemon,
            function_name='register',
            args=['name', 'plugin']
        )
