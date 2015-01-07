#########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
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
import logging
import getpass
import tempfile
import os

from cloudify.utils import setup_default_logger


class BaseTestCase(testtools.TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.logger = setup_default_logger(
            'cloudify.agent.tests',
            level=logging.DEBUG)
        self.username = getpass.getuser()
        self.temp_folder = tempfile.mkdtemp(prefix='cloudify-agent-tests-')
        self.temp_file = tempfile.mkstemp(prefix='cloudify-agent-tests-')
        self.currdir = os.getcwd()
        os.chdir(self.temp_folder)

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        os.chdir(self.currdir)

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
