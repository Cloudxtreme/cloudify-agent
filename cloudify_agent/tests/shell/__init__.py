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

import sys
from cloudify_agent.shell import cli
from mock import patch

from cloudify_agent.tests import BaseTestCase


class BaseCommandLineTestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseCommandLineTestCase, cls).setUpClass()

    def _run(self, command):
        sys.argv = command.split()
        cli.main()

    def assert_method_called(self,
                             cli_command,
                             module,
                             function_name,
                             kwargs):
        with patch.object(module, function_name) as mock:
            try:
                self._run(cli_command)
            except BaseException as e:
                self.logger.info(str(e))
            mock.assert_called_with(**kwargs)


