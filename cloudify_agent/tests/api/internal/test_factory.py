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

from cloudify_agent.api.internal.daemon.factory import DaemonFactory
from cloudify_agent.tests.api import BaseApiTestCase
from cloudify_agent.tests.api import CLOUDIFY_STORAGE_FOLDER
from cloudify_agent.tests.api import SudoLessLocalCommandRunner
from cloudify_agent.tests.api import patch_unless_travis
from cloudify_agent.tests.api import travis


@patch_unless_travis('cloudify_agent.api.internal.daemon.factory.CLOUDIFY_AGENT_STORAGE',  # NOQA
                     CLOUDIFY_STORAGE_FOLDER)
@patch_unless_travis('cloudify_agent.api.internal.daemon.factory.LocalCommandRunner',  # NOQA
                     SudoLessLocalCommandRunner)
class TestDaemonFactory(BaseApiTestCase):

    def test_create_initd(self):
        daemon = DaemonFactory.create(
            process_management='init.d',
            name='name',
            queue='queue',
            manager_ip='127.0.0.1',
            host='127.0.0.1',
            user='user',
            optional1='optional1',
            optional2='optional2')
        self.assertEqual('name', daemon.name)
        self.assertEqual('queue', daemon.queue)
        self.assertEqual('127.0.0.1', daemon.manager_ip)
        self.assertEqual('127.0.0.1', daemon.host)
        self.assertEqual('user', daemon.user)
        self.assertEqual(
            {
                'optional1': 'optional1',
                'optional2': 'optional2'
            },
            daemon.optional_parameters)

    def test_create_relocated(self):
        if not travis():
            raise RuntimeError('Error! This test cannot be executed '
                               'outside of the travis CI '
                               'system since it may corrupt '
                               'your local virtualenv')
        daemon = DaemonFactory.create(
            process_management='init.d',
            name='name',
            queue='queue',
            manager_ip='127.0.0.1',
            host='127.0.0.1',
            user='user',
            relocated=True)
        self.assertEqual('name', daemon.name)
        self.assertEqual('queue', daemon.queue)
        self.assertEqual('127.0.0.1', daemon.manager_ip)
        self.assertEqual('127.0.0.1', daemon.host)
        self.assertEqual('user', daemon.user)

    def test_save_load_delete(self):

        name = 'name-{0}'.format(str(uuid.uuid4())[0:4])
        daemon = DaemonFactory.create(
            process_management='init.d',
            name=name,
            queue='queue',
            manager_ip='127.0.0.1',
            host='127.0.0.1',
            user='user',
            optional1='optional1',
            optional2='optional2')

        DaemonFactory.save(daemon)
        loaded = DaemonFactory.load(name)
        self.assertEqual('init.d', loaded.PROCESS_MANAGEMENT)
        self.assertEqual(name, loaded.name)
        self.assertEqual('queue', loaded.queue)
        self.assertEqual('127.0.0.1', loaded.manager_ip)
        self.assertEqual('127.0.0.1', loaded.host)
        self.assertEqual('user', loaded.user)
        self.assertEqual(
            {
                'optional1': 'optional1',
                'optional2': 'optional2'
            },
            loaded.optional_parameters)
        DaemonFactory.delete(daemon)
        self.assertRaises(IOError, DaemonFactory.load, daemon)

    def test_load_non_existing(self):
        self.assertRaises(IOError,
                          DaemonFactory.load,
                          'non_existing_name')
