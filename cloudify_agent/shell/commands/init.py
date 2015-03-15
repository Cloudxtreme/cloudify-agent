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

import click

from cloudify_agent.shell import utils
from cloudify_agent.shell.main import handle_failures


@click.command()
@click.option('--logfile',
              help='Path to a file where logs will be recorded',
              required=False)
@handle_failures
def init(logfile):

    """
    Creates the cloudify-agent logging configuration file inside the
    working directory
    """

    click.echo('Initializing...')
    utils.initialize(logfile)
    click.echo('Successfully initialized cloudify-agent')
