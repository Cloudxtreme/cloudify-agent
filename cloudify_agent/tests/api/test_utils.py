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

import json
import os

from cloudify_agent.api.utils import render_template
from cloudify_agent.tests.api import BaseApiTestCase


class TestUtils(BaseApiTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUtils, cls).setUpClass()
        if 'TRAVIS_BUILD_DIR' not in os.environ \
                and 'FORCE_TESTS' not in os.environ:
            raise RuntimeError(
                'Error! These tests require sudo '
                'permissions and may manipulate system wide files. '
                'Therefore they are only executed on the travis CI system. '
                'If you are ABSOLUTELY sure you wish to '
                'run them on your local box, set the FORCE_TESTS '
                'environment variable to bypass this restriction.')

    def test_render_template(self):

        template = '{"name": "{{ name }}"}'
        values = {'name': 'test_name'}

        file_path = render_template(template, **values)
        rendered = json.load(open(file_path))
        self.assertEqual(rendered['name'], 'test_name')
