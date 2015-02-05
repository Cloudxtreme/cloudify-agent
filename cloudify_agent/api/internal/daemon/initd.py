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

import os
import time

from cloudify.utils import LocalCommandRunner

from cloudify_agent.included_plugins import included_plugins
from cloudify_agent.api import utils
from cloudify_agent.api.internal.daemon.base import Daemon
from cloudify_agent.api import defaults
from cloudify_agent import VIRTUALENV


class GenericLinuxDaemon(Daemon):

    SCRIPT_DIR = '/etc/init.d'
    CONFIG_DIR = '/etc/default'
    PROCESS_MANAGEMENT = 'init.d'

    def __init__(self, **params):
        super(GenericLinuxDaemon, self).__init__(**params)

        # init.d specific configuration
        self.script_path = os.path.join(self.SCRIPT_DIR, self.name)
        self.config_path = os.path.join(self.CONFIG_DIR, self.name)
        self.includes_file_path = os.path.join(
            self.workdir,
            '{0}-includes'.format(self.name)
        )

    def create(self):
        self._validate_create()
        self._create_includes()
        self._create_script()
        self._create_config()

    def start(self,
              interval=defaults.START_INTERVAL,
              timeout=defaults.STOP_TIMEOUT):
        self.runner.sudo(start_command(self))
        end_time = time.time() + timeout
        while time.time() < end_time:
            stats = self._get_worker_stats()
            if stats:
                return
            time.sleep(interval)
        self._verify_no_celery_error()
        raise RuntimeError('Failed starting agent. '
                           'waited for {0} seconds.'
                           .format(timeout))

    def stop(self,
             interval=defaults.STOP_TIMEOUT,
             timeout=defaults.STOP_TIMEOUT):
        self.runner.sudo(stop_command(self))
        end_time = time.time() + timeout
        while time.time() < end_time:
            stats = self._get_worker_stats()
            if not stats:
                return
            time.sleep(interval)
        self._verify_no_celery_error()
        raise RuntimeError('Failed stopping Cloudify agent. '
                           'waited for {0} seconds.'
                           .format(timeout))

    def delete(self):
        self._validate_delete()
        self.runner.sudo('rm {0}'.format(self.script_path))
        self.runner.sudo('rm {0}'.format(self.config_path))
        self.runner.sudo('rm {0}'.format(self.includes_file_path))

    def register(self, plugin):
        plugin_paths = self._list_plugin_files(plugin)

        with open(self.includes_file_path) as include_file:
            includes = include_file.read()
        new_includes = '{0},{1}'.format(includes, ','.join(plugin_paths))

        if os.path.exists(self.includes_file_path):
            os.remove(self.includes_file_path)

        with open(self.includes_file_path, 'w') as f:
            f.write(new_includes)

    def restart(self):
        self.stop()
        self.start()

    @staticmethod
    def _list_plugin_files(plugin_name):

        """
        Retrieves python files related to the plugin.
        __init__ file are filtered out.

        :param plugin_name: The plugin name.
        :type plugin_name: string

        :return: A list of file paths.
        :rtype `list of str`
        """

        module_paths = []
        runner = LocalCommandRunner()
        files = runner.run(
            '{0}/bin/pip show -f {1}'
            .format(VIRTUALENV, plugin_name)
        ).output.splitlines()
        for module in files:
            if module.endswith('.py') and '__init__' not in module:
                # the files paths are relative to the
                # package __init__.py file.
                module_paths.append(
                    module.replace('../', '')
                    .replace('/', '.').replace('.py', '').strip())
        return module_paths

    def _validate_delete(self):
        stats = self._get_worker_stats()
        if stats:
            raise RuntimeError(
                'Cannot delete daemon {0}. Process is still running'
                .format(self.name))

    def _validate_create(self):

        def validate(path):
            if os.path.exists(path):
                raise RuntimeError(
                    'Cannot create daemon {0}. {1} already exists.'
                    .format(self.name, path))

        validate(self.script_path)
        validate(self.config_path)
        validate(self.includes_file_path)

    def _create_includes(self):

        """
        Creates an includes file which contains the modules
        of the built-in plugins. These modules will be imported and
        all containing operations will be registered.

        """

        directory = os.path.dirname(self.includes_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.includes_file_path, 'w') as f:
            includes = []
            for plugin in included_plugins:
                includes.extend(self._list_plugin_files(plugin))
            f.write(','.join(includes))

    def _create_script(self):

        """
        Creates the daemon init script to be placed under /etc/init.d
        Uses the template 'resources/celeryd.template'.

        """

        rendered = utils.rendered_template_to_tempfile(
            template_path='celeryd.template',
            daemon_name=self.name,
            config_path=self.config_path
        )
        self.runner.sudo('cp {0} {1}'.format(rendered, self.script_path))
        self.runner.sudo('rm {0}'.format(rendered))
        self.runner.sudo('chmod +x {0}'.format(self.script_path))

    def _create_config(self):

        """
        Creates the daemon configuration file. Will be placed under /etc/default
        Uses the template 'resources/celeryd.conf.template'.

        """

        rendered = utils.rendered_template_to_tempfile(
            template_path='celeryd.conf.template',
            queue=self.queue,
            workdir=self.workdir,
            manager_ip=self.manager_ip,
            manager_port=self.manager_port,
            host=self.host,
            broker_url=self.broker_url,
            user=self.user,
            min_workers=self.min_workers,
            max_workers=self.max_workers,
            includes_file_path=self.includes_file_path,
            virtualenv_path=VIRTUALENV
        )

        self.runner.sudo('cp {0} {1}'.format(rendered, self.config_path))
        self.runner.sudo('rm {0}'.format(rendered))

    def _verify_no_celery_error(self):

        """
        Verifies no error was raised on celery startup.

        """

        error_file_path = os.path.join(
            self.workdir,
            'celery_error.out')

        # this means the celery worker had an uncaught
        # exception and it wrote its content
        # to the file above because of our custom exception
        # handler (see app.py)
        if os.path.exists(error_file_path):
            with open(error_file_path) as f:
                error = f.read()
            os.remove(error_file_path)
            raise RuntimeError(error)

    def _get_worker_stats(self):
        destination = 'celery.{0}'.format(self.queue)
        inspect = self.celery.control.inspect(
            destination=[destination])
        stats = (inspect.stats() or {}).get(destination)
        return stats


def start_command(daemon):
    return 'service {0} start'.format(daemon.name)


def stop_command(daemon):
    return 'service {0} stop'.format(daemon.name)
