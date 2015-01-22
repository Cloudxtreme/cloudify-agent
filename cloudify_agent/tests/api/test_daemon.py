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

from mock import patch

from cloudify_agent.tests.api import BaseApiTestCase
from cloudify_agent.api import daemon as api


@patch('cloudify_agent.api.daemon.DaemonFactory')
class TestApi(BaseApiTestCase):

    def test_create(self, factory):
        api.create(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='Whatever'
        )
        factory_create = factory.create
        factory_save = factory.save
        daemon = factory_create.return_value

        factory_create.assert_called_once_with(
            name=self.name,
            queue=self.queue,
            agent_ip='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            process_management='Whatever'
        )
        daemon.create.assert_called_once_with()
        factory_save.assert_called_once_with(daemon)

    def test_start(self, factory):
        api.start(self.name)
        factory_load = factory.load
        daemon = factory_load.return_value

        factory_load.assert_called_once_with(self.name)
        daemon.start.assert_called_once_with(
            interval=1, timeout=15
        )

    def test_stop(self, factory):
        api.stop(self.name)
        factory_load = factory.load
        daemon = factory_load.return_value

        factory_load.assert_called_once_with(self.name)
        daemon.stop.assert_called_once_with(
            interval=1, timeout=15
        )

    def test_register(self, factory):
        api.register(self.name, 'mock-plugin')
        factory_load = factory.load
        daemon = factory_load.return_value

        factory_load.assert_called_once_with(self.name)
        daemon.register.assert_called_once_with('mock-plugin')

    def test_delete(self, factory):
        api.delete(self.name)
        factory_load = factory.load
        daemon = factory_load.return_value

        factory_load.assert_called_once_with(self.name)
        daemon.delete.assert_called_once_with()

    def test_restart(self, factory):
        api.restart(self.name)
        factory_load = factory.load
        daemon = factory_load.return_value

        factory_load.assert_called_once_with(self.name)
        daemon.restart.assert_called_once_with()
