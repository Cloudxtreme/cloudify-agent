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

import testtools
import os

from cloudify_agent.api.internal.daemon.base import Daemon


class TestDaemon(testtools.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestDaemon, cls).setUpClass()
        cls.daemon = Daemon(
            name='name',
            queue='queue',
            host='queue',
            manager_ip='manager_ip',
            user='user'
        )

    def test_default_basedir(self):
        self.assertEqual(os.getcwd(), self.daemon.workdir)

    def test_default_manager_port(self):
        self.assertEqual(80, self.daemon.manager_port)

    def test_default_min_workers(self):
        self.assertEqual(0, self.daemon.min_workers)

    def test_default_max_workers(self):
        self.assertEqual(5, self.daemon.max_workers)

    def test_default_broker_url(self):
        self.assertEqual('amqp://guest:guest@manager_ip:5672//',
                         self.daemon.broker_url)
