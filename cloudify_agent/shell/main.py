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

import sys
from functools import wraps

import click

from cloudify_agent.api import exceptions as api_exceptions
from cloudify_agent.api import errors as api_errors
from cloudify_agent.shell import exceptions as cli_exceptions
from cloudify_agent.shell import errors as cli_errors
from cloudify_agent.shell import utils


codes = {

    # exception start from 101
    api_exceptions.DaemonException: 101,
    api_exceptions.DaemonShutdownTimeout: 102,
    api_exceptions.DaemonStartupTimeout: 103,
    api_exceptions.DaemonStillRunningException: 104,
    cli_exceptions.CloudifyAgentNotFoundException: 105,
    cli_exceptions.CloudifyAgentException: 100,

    # errors start from 201
    api_errors.DaemonError: 201,
    api_errors.DaemonParametersError: 202,
    api_errors.DaemonConfigurationError: 203,
    api_errors.MissingMandatoryParamError: 204,
    cli_errors.CloudifyAgentNotImplementedError: 205,
    cli_errors.CloudifyAgentError: 200
}


def handle_failures(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except BaseException as e:
            tpe, value, tb = sys.exc_info()

            if isinstance(e, api_exceptions.DaemonException):

                # convert api exceptions to cli exceptions.
                value = cli_exceptions.CloudifyAgentException(str(e))
            if isinstance(e, api_errors.DaemonError):

                # convert api errors to cli errors
                value = cli_errors.CloudifyAgentError(str(e))

            # in any case, set the exception exit_code accordingly
            value.exit_code = codes.get(tpe, 1)
            raise type(value), value, tb

    return wrapper


@click.group()
@click.option('--debug', default=False, is_flag=True)
def main(debug):
    utils.setup_loggers(debug)


@click.group('daemon')
def daemon_sub_command():
    pass


# adding all of our commands.

from cloudify_agent.shell.commands import init, daemon
from cloudify_agent.shell.commands import configure

main.add_command(init.init)
main.add_command(configure.configure)

daemon_sub_command.add_command(daemon.create)
daemon_sub_command.add_command(daemon.configure)
daemon_sub_command.add_command(daemon.start)
daemon_sub_command.add_command(daemon.stop)
daemon_sub_command.add_command(daemon.delete)
daemon_sub_command.add_command(daemon.restart)
daemon_sub_command.add_command(daemon.register)

main.add_command(daemon_sub_command)
