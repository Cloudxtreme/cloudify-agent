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

import os

import cloudify_agent
from cloudify_agent.api import utils
from cloudify_agent.tests.api import BaseApiTestCase


class TestUtils(BaseApiTestCase):

    def test_get_resource(self):
        resource = utils.get_resource('celeryd.conf.template')
        path_to_resource = os.path.join(
            os.path.dirname(cloudify_agent.__file__),
            'resources',
            'celeryd.conf.template'
        )
        with open(path_to_resource) as f:
            self.assertEqual(f.read(), resource)

    def test_rendered_template_to_tempfile(self):
        tempfile = utils.rendered_template_to_tempfile(
            template_path='celeryd.conf.template',
            workdir='workdir'
        )
        with open(tempfile) as f:
            rendered = f.read()
            self.assertIn('CELERY_WORK_DIR="workdir"', rendered)

    def test_resource_to_tempfile(self):
        tempfile = utils.resource_to_tempfile(
            resource_path='celeryd.conf.template'
        )
        path_to_resource = os.path.join(
            os.path.dirname(cloudify_agent.__file__),
            'resources',
            'celeryd.conf.template'
        )
        with open(path_to_resource) as expected:
            with open(tempfile) as actual:
                self.assertEqual(expected.read(),
                                 actual.read())

    def test_content_to_tempfile(self):
        tempfile = utils.content_to_tempfile(
            content='content'
        )
        with open(tempfile) as f:
            self.assertEqual('content', f.read())
