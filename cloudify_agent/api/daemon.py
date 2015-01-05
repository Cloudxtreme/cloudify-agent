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
import logging
import sys
from jinja2 import Template

import cloudify_agent
from cloudify.utils import LocalCommandRunner
from cloudify.utils import setup_default_logger
from cloudify_agent.included_plugins import included_plugins
from cloudify_agent.api import utils


def create(queue, ip, manager_ip, user, **optional_parameters):
    daemon = GenericLinuxDaemon(
        queue=queue,
        **optional_parameters
    )
    daemon.create(ip=ip,
                  manager_ip=manager_ip,
                  user=user)
    return daemon


def register(queue, plugin, **optional_parameters):
    daemon = GenericLinuxDaemon(
        queue=queue,
        **optional_parameters
    )
    daemon.register(plugin)


class GenericLinuxDaemon(object):

    SCRIPT_DIR = '/etc/init.d'
    CONFIG_DIR = '/etc/default'

    def __init__(self, queue,
                 **optional_parameters):
        self.name = 'celeryd-{0}'.format(queue)

        # Mandatory arguments
        self.queue = queue

        # optional parameters with default values
        self.basedir = optional_parameters.get('basedir') or os.getcwd()
        self.broker_port = optional_parameters.get('broker_port') or 5672
        self.manager_port = optional_parameters.get('manager_port') or 80
        self.autoscale = optional_parameters.get('autoscale') or '0,5'

        # configure logger
        self.logger = setup_default_logger('cloudify.agent.generic-daemon-{0}'
                                           .format(self.name),
                                           level=logging.INFO)

        # save for future reference
        self.optional_parameters = optional_parameters

        # init.d specific configuration
        self.script_path = os.path.join(self.SCRIPT_DIR, self.name)
        self.config_path = os.path.join(self.CONFIG_DIR, self.name)
        self.virtualenv_path = os.path.dirname(os.path.dirname(sys.executable))

        # create necessary files and directories
        self.includes_file_path = os.path.join(self.CONFIG_DIR,
                                               '{0}-includes'.format(self.name))

    def _run(self, command):
        runner = LocalCommandRunner(logger=self.logger)
        return runner.run(command)

    def _create_includes_file(self):

        """
        Creates an includes file which contains the modules
        of the built-in plugins. These modules will imported and registered.

        :return: The path to the file.
        """

        # first write the content to a temp file
        temp_includes = tempfile.mkstemp()[1]
        with open(temp_includes, 'w') as f:
            includes = []
            for plugin in included_plugins:
                includes.extend(utils.extract_module_paths_from_name(self.virtualenv_path,
                                                                     plugin))
            f.write(','.join(includes))

        # now move it using sudo
        self._run('sudo cp {0} {1}'.format(temp_includes, self.includes_file_path))

    def _validate_create(self):

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

    def create(self, ip, manager_ip, user):
        self._validate_create()
        self._create_includes_file()
        self._create_script()
        self._create_config(ip=ip,
                            manager_ip=manager_ip,
                            user=user)

    def register(self, plugin):
        plugin_paths = utils.extract_module_paths_from_name(self.virtualenv_path,
                                                            plugin)
        # the includes file is in a restricted directory
        # must use sudo to read it.
        response = self._run('sudo cat {0}'.format(self.includes_file_path))
        includes = response.std_out
        self.logger.debug('Adding tasks: {0}'.format(includes))
        new_includes = '{0},{1}'.format(includes, ','.join(plugin_paths))

        # first write the content to a temp file
        temp_includes = tempfile.mkstemp()[1]
        with open(temp_includes, 'w') as f:
            f.write(new_includes)

        # now move it using sudo
        self._run('sudo rm {0}'.format(self.includes_file_path))
        self._run('sudo cp {0} {1}'.format(temp_includes, self.includes_file_path))

    def _create_script(self):
        celeryd = pkg_resources.resource_string(
            cloudify_agent.__name__,
            'resources/celeryd.template')
        template = Template(celeryd)
        rendered = template.render(daemon_name=self.name)
        temp = tempfile.mkstemp(prefix=self.name,
                                text=True)
        with open(temp[1], 'w') as f:
            f.write(rendered)
            f.write(os.linesep)

        # place the init script under the /etc/init.d directory.
        self._run('sudo cp {0} {1}'.format(temp[1], self.script_path))
        self._run('sudo chmod +x {0}'.format(self.script_path))

    def _create_config(self, ip, manager_ip, user):

        group = self.optional_parameters.get('group') or user
        broker_ip = self.optional_parameters.get('broker_ip') or manager_ip

        self.work_dir = os.path.join(self.basedir, self.name, 'work')
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

        celeryd_conf = pkg_resources.resource_string(
            cloudify_agent.__name__,
            'resources/celeryd.conf.template')
        template = Template(celeryd_conf)
        rendered = template.render(
            queue=self.queue,
            work_dir=self.work_dir,
            manager_ip=manager_ip,
            manager_port=self.manager_port,
            agent_ip=ip,
            broker_ip=broker_ip,
            broker_port=self.broker_port,
            group=group,
            user=user,
            autoscale=self.autoscale,
            includes_file_path=self.includes_file_path,
            virtualenv_path=self.virtualenv_path)
        temp = tempfile.mkstemp(prefix=self.name,
                                text=True)
        with open(temp[1], 'w') as f:
            f.write(rendered)
            f.write(os.linesep)

        # place the config file under the /etc/default directory.
        self._run('sudo cp {0} {1}'.format(temp[1], self.config_path))
