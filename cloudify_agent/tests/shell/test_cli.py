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

import click

from cloudify_agent.tests.shell import BaseCommandLineTestCase


class TestCommandLine(BaseCommandLineTestCase):

    def test_exception_hook(self):

        @click.command()
        def raise_error():
            raise RuntimeError('Error')

        from cloudify_agent.shell.cli import main
        main.add_command(raise_error, 'raise-error')
        try:
            self._run('cloudify-agent raise-error')
        except RuntimeError:
            import sys
            output = sys.excepthook(*sys.exc_info())
            self.assertEqual('[FATAL] Error', output)
