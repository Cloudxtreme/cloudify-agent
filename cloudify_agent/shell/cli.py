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
import click
import logging
import StringIO
import traceback

from celery import __main__
from cloudify.utils import setup_default_logger

from cloudify_agent.shell.subcommands import daemon


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    _set_logger(debug)
    _set_exception_hook(debug)


@click.command()
@click.argument('celery-args', nargs=-1)
def worker(celery_args):
    sys.argv = ['celery', 'worker']
    sys.argv.extend(celery_args)
    __main__.main()


@click.group('daemon')
def daemon_sub_command():
    pass


main.add_command(daemon_sub_command)
main.add_command(worker)

daemon_sub_command.add_command(daemon.create)
daemon_sub_command.add_command(daemon.start)
daemon_sub_command.add_command(daemon.stop)
daemon_sub_command.add_command(daemon.restart)
daemon_sub_command.add_command(daemon.delete)
daemon_sub_command.add_command(daemon.register)


def _set_logger(debug):

    level = logging.DEBUG if debug else logging.INFO

    # we change the format of the api logging
    # to be more shell like.
    from cloudify_agent.api.internal.base import LOGGER_NAME
    setup_default_logger(LOGGER_NAME,
                         level=level,
                         fmt='%(message)s')


def _set_exception_hook(debug):

    def exception_hook(tpe, value, tb):
        output = '[FATAL] {0}'.format(str(value))

        if debug:
            # print traceback if verbose
            s_traceback = StringIO.StringIO()
            traceback.print_exception(
                etype=tpe,
                value=value,
                tb=tb,
                file=s_traceback)
            output = s_traceback.getvalue()
            click.echo(output)
        else:
            click.secho(output, fg='red')
        return output

    sys.excepthook = exception_hook
