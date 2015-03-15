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

from cloudify_agent.tests.shell.commands import BaseCommandLineTestCase


@patch('cloudify_agent.shell.commands.daemon.DaemonFactory')
class TestDaemonCommandLine(BaseCommandLineTestCase):

    PROCESS_MANAGEMENT = 'init.d'

    def test_create(self, factory):
        self._run('cloudify-agent daemon create --name=name '
                  '--queue=queue --host=127.0.0.1 '
                  '--manager-ip=127.0.0.1 --user=user')

        factory_new = factory.new
        factory_new.assert_called_once_with(
            name='name',
            queue='queue',
            host='127.0.0.1',
            user='user',
            manager_ip='127.0.0.1',
            process_management='init.d',
            broker_ip=None,
            workdir=None,
            broker_url=None,
            max_workers=None,
            min_workers=None,
            broker_port=None,
            manager_port=None
        )

        daemon = factory_new.return_value
        daemon.create.assert_called_once_with()

        factory_save = factory.save
        factory_save.assert_called_once_with(daemon)

    def test_configure(self, factory):
        self._run('cloudify-agent daemon configure --name=name')

        factory_load = factory.load
        factory_load.assert_called_once_with('name')

        daemon = factory_load.return_value
        daemon.configure.assert_called_once_with()

    def test_start(self, factory):
        self._run('cloudify-agent daemon start --name=name '
                  '--interval 5 --timeout 20')

        factory_load = factory.load
        factory_load.assert_called_once_with('name')

        daemon = factory_load.return_value
        daemon.start.assert_called_once_with(
            interval=5,
            timeout=20
        )

    def test_stop(self, factory):
        self._run('cloudify-agent daemon stop --name=name '
                  '--interval 5 --timeout 20')

        factory_load = factory.load
        factory_load.assert_called_once_with('name')

        daemon = factory_load.return_value
        daemon.stop.assert_called_once_with(
            interval=5,
            timeout=20
        )

    def test_delete(self, factory):
        self._run('cloudify-agent daemon delete --name=name')

        factory_load = factory.load
        factory_load.assert_called_once_with('name')

        daemon = factory_load.return_value
        daemon.delete.assert_called_once_with()

    def test_restart(self, factory):
        self._run('cloudify-agent daemon restart --name=name')

        factory_load = factory.load
        factory_load.assert_called_once_with('name')

        daemon = factory_load.return_value
        daemon.restart.assert_called_once_with()

    def test_register(self, factory):
        self._run('cloudify-agent daemon register '
                  '--name=name --plugin=plugin')

        factory_load = factory.load
        factory_load.assert_called_once_with('name')

        daemon = factory_load.return_value
        daemon.register.assert_called_once_with('plugin')

    def test_required(self, _):
        self._run('cloudify-agent daemon create --manager-ip=manager '
                  '--user=user')