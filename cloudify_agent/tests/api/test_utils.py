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
from cloudify_agent.api.utils import dump_daemon_context
from cloudify_agent.api.utils import load_daemon_context

from cloudify_agent.tests.api import BaseApiTestCase


class TestUtils(BaseApiTestCase):

    def test_render_template(self):

        template = '{"name": "{{ name }}"}'
        values = {'name': 'test_name'}

        file_path = render_template(template, **values)
        rendered = json.load(open(file_path))
        self.assertEqual(rendered['name'], 'test_name')

    def test_load_existing_daemon_context(self):
        dumped_context = {'a': 'value_a'}
        dump_daemon_context('test_queue', context=dumped_context)
        loaded_context = load_daemon_context('test_queue')
        self.assertEqual(dumped_context, loaded_context)

    def test_load_non_existing_daemon_context(self):
        self.assertRaises(RuntimeError, load_daemon_context, 'test_queue')

    def test_dump_daemon_context(self):
        dumped_context = {'a': 'value_a'}
        dump_daemon_context('test_queue', context=dumped_context)
        context_path = os.path.join(os.getcwd(), '.cloudify-agent',
                                    'test_queue.json')
        loaded_context = json.load(open(context_path))
        self.assertEqual(dumped_context, loaded_context)
