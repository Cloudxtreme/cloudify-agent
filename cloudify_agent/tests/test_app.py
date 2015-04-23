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
import tempfile
import testtools


class TestApp(testtools.TestCase):

    def test_broker_url_from_env(self):
        os.environ['CELERY_BROKER_URL'] = 'test-url'
        from cloudify_agent import app
        self.assertEqual(app.broker_url, 'test-url')

    def test_broker_url_default(self):
        from cloudify_agent import app
        self.assertEqual(app.broker_url, 'amqp://')

    def test_work_folder(self):
        os.environ['CELERYD_WORK_DIR'] = 'test-folder'
        from cloudify_agent import app
        self.assertEqual(app.work_folder, 'test-folder')

    def test_app(self):
        os.environ['CELERY_BROKER_URL'] = 'test-url'
        from cloudify_agent import app
        self.assertEqual(app.app.conf['BROKER_URL'], 'test-url')
        self.assertEqual(app.app.conf['CELERY_RESULT_BACKEND'], 'test-url')

    def test_exception_hook(self):
        os.environ['CELERYD_WORK_DIR'] = tempfile.mkdtemp()
        from cloudify_agent import app
        import sys
        sys.excepthook(Exception, Exception('Error'), None)
        work_folder = app.work_folder

        # check file was created with the exception details
        error_file = os.path.join(work_folder, 'celery_error.out')
        self.assertTrue(os.path.exists(error_file))

        with open(error_file) as f:
            content = f.read()
        self.assertTrue("Type: <type 'exceptions.Exception'>" in content)
        self.assertTrue("Value: Error" in content)
