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
import sys
from mock import patch

from cloudify_agent.shell import cli


class BaseCommandLineTestCase(testtools.TestCase):

    def _run(self, command):
        sys.argv = command.split()
        try:
            cli.main()
        except SystemExit:
            pass

    def assert_function_called(self, cli_command, module, function_name,
                               args=None, kwargs=None):
        if not kwargs:
            kwargs = {}
        if not args:
            args = []
        with patch.object(module, function_name) as mock:
            self._run(cli_command)
            mock.assert_called_with(*args, **kwargs)

    def _run_patched(self, cli_command, module, function_name):
        with patch.object(module, function_name):
            self._run(cli_command)
