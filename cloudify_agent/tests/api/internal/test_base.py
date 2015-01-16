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
import os

from cloudify_agent.api.internal.base import DaemonFactory
from cloudify_agent.api.internal.base import Daemon
from cloudify_agent.tests.api import BaseApiTestCase


class TestDaemonFactory(BaseApiTestCase):

    def test_create(self):
        daemon = DaemonFactory.create(
            process_management='init.d',
            name='name',
            queue='queue',
            manager_ip='127.0.0.1',
            agent_ip='127.0.0.1',
            user='user',
            optional1='optional1',
            optional2='optional2')
        self.assertEqual('name', daemon.name)
        self.assertEqual('queue', daemon.queue)
        self.assertEqual('127.0.0.1', daemon.manager_ip)
        self.assertEqual('127.0.0.1', daemon.agent_ip)
        self.assertEqual('user', daemon.user)
        self.assertEqual(
            {
                'optional1': 'optional1',
                'optional2': 'optional2'
            },
            daemon.optional_parameters)

    def test_save_load_delete(self):

        name = 'name-{0}'.format(str(uuid.uuid4())[0:4])
        daemon = DaemonFactory.create(
            process_management='init.d',
            name=name,
            queue='queue',
            manager_ip='127.0.0.1',
            agent_ip='127.0.0.1',
            user='user',
            optional1='optional1',
            optional2='optional2')

        DaemonFactory.save(daemon)
        loaded = DaemonFactory.load(name)
        self.assertEqual('init.d', loaded.PROCESS_MANAGEMENT)
        self.assertEqual(name, loaded.name)
        self.assertEqual('queue', loaded.queue)
        self.assertEqual('127.0.0.1', loaded.manager_ip)
        self.assertEqual('127.0.0.1', loaded.agent_ip)
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


class TestDaemon(BaseApiTestCase):

    def setUp(self):
        super(TestDaemon, self).setUp()
        self.daemon = Daemon(
            name=None,
            queue=None,
            agent_ip=None,
            manager_ip=None,
            user=None
        )

    def test_default_basedir(self):
        self.assertEqual(os.getcwd(), self.daemon.workdir)

    def test_default_broker_port(self):
        self.assertEqual(5672, self.daemon.broker_port)

    def test_default_manager_port(self):
        self.assertEqual(80, self.daemon.manager_port)

    def test_default_autoscale(self):
        self.assertEqual('0,5', self.daemon.autoscale)
