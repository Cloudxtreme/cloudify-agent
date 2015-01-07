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

import pkg_resources
import tempfile
import os
import sys
import logging


from cloudify.utils import setup_default_logger
from cloudify.utils import LocalCommandRunner

import cloudify_agent
from cloudify_agent.included_plugins import included_plugins
from cloudify_agent.api import utils


LOGGER_NAME = 'cloudify.agent.api.daemon'

logger = setup_default_logger(LOGGER_NAME,
                              level=logging.INFO)


def create(queue, agent_ip, manager_ip, user, process_management,
           **optional_parameters):

    daemon = HANDLERS[process_management](
        queue=queue,
        **optional_parameters
    )
    daemon.create(agent_ip=agent_ip,
                  manager_ip=manager_ip,
                  user=user)
    utils.dump_daemon_context(
        queue,
        context={
            'process_management': process_management
        }
    )
    return daemon


def register(queue, plugin):
    context = utils.load_daemon_context(queue)
    daemon = HANDLERS[context['process_management']](
        queue=queue
    )
    daemon.register(plugin)


class Daemon(object):

    def __init__(self, queue, **optional_parameters):

        self.name = 'cloudify-agent-{0}'.format(queue)

        # Mandatory arguments
        self.queue = queue

        # optional parameters with default values
        self.workdir = optional_parameters.get('workdir') or os.getcwd()
        self.broker_port = optional_parameters.get('broker_port') or 5672
        self.manager_port = optional_parameters.get('manager_port') or 80
        self.autoscale = optional_parameters.get('autoscale') or '0,5'

        # configure logger
        self.logger = logger

        # save for future reference
        self.optional_parameters = optional_parameters

    def create(self, agent_ip, manager_ip, user):
        raise NotImplementedError('Must be implemented by subclass')

    def register(self, plugin):
        raise NotImplementedError('Must be implemented by subclass')

    def delete(self):
        raise NotImplementedError('Must be implemented by subclass')

    @staticmethod
    def _extract_module_paths_from_name(virtualenv_path, plugin_name):
        module_paths = []
        runner = LocalCommandRunner()
        files = runner.run(
            '{0}/bin/pip show -f {1}'
            .format(virtualenv_path, plugin_name)
        ).std_out.splitlines()
        for module in files:
            if module.endswith('.py') and '__init__' not in module:
                # the files paths are relative to the package __init__.py file.
                module_paths.append(
                    module.replace('../', '')
                    .replace('/', '.').replace('.py', '').strip())
        return module_paths


class GenericLinuxDaemon(Daemon):

    SCRIPT_DIR = '/etc/init.d'
    CONFIG_DIR = '/etc/default'

    def __init__(self, queue, **optional_parameters):
        super(GenericLinuxDaemon, self).__init__(queue, **optional_parameters)

        # init.d specific configuration
        self.script_path = os.path.join(self.SCRIPT_DIR, self.name)
        self.config_path = os.path.join(self.CONFIG_DIR, self.name)
        self.virtualenv_path = os.path.dirname(os.path.dirname(sys.executable))
        self.includes_file_path = os.path.join(
            self.CONFIG_DIR,
            '{0}-includes'.format(self.name))

    def create(self, agent_ip, manager_ip, user):
        self._validate_create()
        self._create_includes_file()
        self._create_script()
        self._create_config(agent_ip=agent_ip,
                            manager_ip=manager_ip,
                            user=user)

    def register(self, plugin):
        plugin_paths = self._extract_module_paths_from_name(
            self.virtualenv_path, plugin
        )

        includes = self._run('sudo cat {0}'
                             .format(self.includes_file_path)).std_out
        new_includes = '{0},{1}'.format(includes, ','.join(plugin_paths))
        self.logger.debug('Adding operations from modules: {0}'
                          .format(plugin_paths))

        temp_includes = tempfile.mkstemp()[1]
        with open(temp_includes, 'w') as f:
            f.write(new_includes)

        self._run('sudo rm {0}'
                  .format(self.includes_file_path))
        self._run('sudo cp {0} {1}'
                  .format(temp_includes, self.includes_file_path))

    def _run(self, command):

        """
        Runts the given command and uses the current logger
        for output.

        :param command: The command to run.
        :return:
        """
        runner = LocalCommandRunner(logger=self.logger)
        return runner.run(command)

    def _create_includes_file(self):

        """
        Creates an includes file which contains the modules
        of the built-in plugins. These modules will imported and registered.

        """

        temp_includes = tempfile.mkstemp()[1]
        with open(temp_includes, 'w') as f:
            includes = []
            for plugin in included_plugins:
                includes.extend(
                    self._extract_module_paths_from_name(
                        self.virtualenv_path, plugin
                    )
                )
            f.write(','.join(includes))

        self._run('sudo cp {0} {1}'.format(temp_includes,
                                           self.includes_file_path))

    def _validate_create(self):

        """
        Validates that creation operation will be successful.

        :raises: RuntimeError
        """

        # currently no support for re-configuring existing daemons.
        # maybe in the future we can do 'reconfigure' and notify the
        # user here that he can run it.

        if os.path.exists(self.script_path):
            raise RuntimeError('Cannot create daemon {0}. {1} already exists.'
                               .format(self.name, self.script_path))

        if os.path.exists(self.config_path):
            raise RuntimeError('Cannot create daemon {0}. {1} already exists.'
                               .format(self.name, self.config_path))

        if os.path.exists(self.includes_file_path):
            raise RuntimeError('Cannot create daemon {0}. {1} already exists.'
                               .format(self.name, self.includes_file_path))

    def _create_script(self):

        """
        Creates the daemon init script to be placed under /etc/init.d
        Uses the template 'resources/celeryd.template'.

        """
        celeryd = pkg_resources.resource_string(
            cloudify_agent.__name__,
            'resources/celeryd.template')

        rendered = utils.render_template(celeryd,
                                         daemon_name=self.name)

        self._run('sudo cp {0} {1}'.format(rendered, self.script_path))
        self._run('sudo chmod +x {0}'.format(self.script_path))

    def _create_config(self, agent_ip, manager_ip, user):

        """
        Creates the daemon configuration file.
        Will be placed under /etc/default
        Uses the template 'resources/celeryd.conf.template'.

        :param agent_ip: The agent ip.
        :param manager_ip: The manager ip.
        :param user: The user.
        :return:
        """

        broker_ip = self.optional_parameters.get('broker_ip') or manager_ip

        celeryd_conf = pkg_resources.resource_string(
            cloudify_agent.__name__,
            'resources/celeryd.conf.template')
        rendered = utils.render_template(
            celeryd_conf,
            queue=self.queue,
            work_dir=self.workdir,
            manager_ip=manager_ip,
            manager_port=self.manager_port,
            agent_ip=agent_ip,
            broker_ip=broker_ip,
            broker_port=self.broker_port,
            user=user,
            autoscale=self.autoscale,
            includes_file_path=self.includes_file_path,
            virtualenv_path=self.virtualenv_path
        )

        self._run('sudo cp {0} {1}'.format(rendered, self.config_path))


HANDLERS = {
    'init.d': GenericLinuxDaemon
}
