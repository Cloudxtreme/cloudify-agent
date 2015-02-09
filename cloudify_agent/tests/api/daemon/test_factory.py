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

import testtools

from cloudify_agent.api.daemon.factory import DaemonFactory
from cloudify_agent.tests.api.daemon import CLOUDIFY_STORAGE_FOLDER
from cloudify_agent.tests.api.daemon import SudoLessLocalCommandRunner
from cloudify_agent.tests.api.daemon import patch_unless_travis
from cloudify_agent.tests.api.daemon import travis


@patch_unless_travis('cloudify_agent.api.daemon.factory.CLOUDIFY_AGENT_STORAGE',  # NOQA
                     CLOUDIFY_STORAGE_FOLDER)
@patch_unless_travis('cloudify_agent.api.daemon.factory.LocalCommandRunner',  # NOQA
                     SudoLessLocalCommandRunner)
class TestDaemonFactory(testtools.TestCase):

    def test_new_initd(self):
        daemon = DaemonFactory.new(
            process_management='init.d',
            name='name',
            queue='queue',
            manager_ip='127.0.0.1',
            host='127.0.0.1',
            user='user',
            broker_url='127.0.0.1')
        self.assertEqual('name', daemon.name)
        self.assertEqual('queue', daemon.queue)
        self.assertEqual('127.0.0.1', daemon.manager_ip)
        self.assertEqual('127.0.0.1', daemon.host)
        self.assertEqual('127.0.0.1', daemon.broker_url)
        self.assertEqual('user', daemon.user)

    def test_new_relocated(self):
        if not travis():
            raise RuntimeError('Error! This test cannot be executed '
                               'outside of the travis CI '
                               'system since it may corrupt '
                               'your local virtualenv')
        daemon = DaemonFactory.new(
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
        daemon = DaemonFactory.new(
            process_management='init.d',
            name=name,
            queue='queue',
            manager_ip='127.0.0.1',
            host='127.0.0.1',
            user='user',
            broker_url='127.0.0.1')

        DaemonFactory.save(daemon)
        loaded = DaemonFactory.load(name)
        self.assertEqual('init.d', loaded.PROCESS_MANAGEMENT)
        self.assertEqual(name, loaded.name)
        self.assertEqual('queue', loaded.queue)
        self.assertEqual('127.0.0.1', loaded.manager_ip)
        self.assertEqual('127.0.0.1', loaded.host)
        self.assertEqual('user', loaded.user)
        self.assertEqual('127.0.0.1', daemon.broker_url)
        DaemonFactory.delete(daemon.name)
        self.assertRaises(IOError, DaemonFactory.load, daemon)

    def test_load_non_existing(self):
        self.assertRaises(IOError,
                          DaemonFactory.load,
                          'non_existing_name')
