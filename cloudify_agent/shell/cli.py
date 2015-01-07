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

from celery import __main__

from cloudify_agent.shell.subcommands import daemon


@click.group()
def main():
    sys.excepthook = exception_hook


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
daemon_sub_command.add_command(daemon.register)


def exception_hook(tpe, value, tb):
    output = '[FATAL] {0}'.format(str(value))
    click.secho(output, fg='red')
    return output
