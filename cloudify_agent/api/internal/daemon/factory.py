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
import json
import tempfile
from cloudify.exceptions import CommandExecutionException

from cloudify.utils import LocalCommandRunner

from cloudify_agent.api.internal.daemon.base import Daemon
from cloudify_agent.api import api_logger
from cloudify_agent import VIRTUALENV
from cloudify_agent import CLOUDIFY_AGENT_STORAGE


class DaemonFactory(object):

    @staticmethod
    def _find_implementation(process_management):

        """
        Locates the proper daemon implementation for the specific
        process management system. For this to work, all implementations
        need to be imported at this time.

        see api/internal/daemon/__init__.py
        """

        daemons = Daemon.__subclasses__()
        for daemon in daemons:
            if daemon.PROCESS_MANAGEMENT == process_management:
                return daemon
        raise RuntimeError('No implementation found for daemon of type: {0}'
                           .format(process_management))

    @staticmethod
    def _fix_env():

        """
        This method is used for auto-configuration of the virtualenv.
        It is needed in case the environment was created using different paths
        than the one that is used at runtime.

        """

        runner = LocalCommandRunner()

        for link in ['archives', 'bin', 'include', 'lib']:
            link_path = '{0}/local/{1}'.format(VIRTUALENV, link)
            try:
                runner.run('unlink {0}'.format(link_path))
                runner.run('ln -s {0}/{1} {2}'
                           .format(VIRTUALENV, link, link_path))
            except CommandExecutionException:
                pass

        bin_dir = '{0}/bin'.format(VIRTUALENV)

        for executable in os.listdir(bin_dir):
            path = os.path.join(bin_dir, executable)
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                lines = f.read().split(os.linesep)
                if lines[0].endswith('/bin/python'):
                    lines[0] = '#!{0}/python'.format(bin_dir)
            with open(path, 'w') as f:
                f.write(os.linesep.join(lines))

    @staticmethod
    def create(process_management,
               name,
               queue,
               manager_ip,
               host,
               user,
               **optional_parameters):
        if optional_parameters.get('relocated'):
            DaemonFactory._fix_env()
        daemon = DaemonFactory._find_implementation(process_management)
        return daemon(
            name=name,
            queue=queue,
            manager_ip=manager_ip,
            host=host,
            user=user,
            **optional_parameters
        )

    @staticmethod
    def load(name):
        daemon_path = os.path.join(
            CLOUDIFY_AGENT_STORAGE,
            '{0}.json'.format(name)
        )
        if not os.path.exists(daemon_path):
            raise IOError('Cannot load daemon: {0} does not exists.'
                          .format(daemon_path))
        runner = LocalCommandRunner(logger=api_logger)
        contents = runner.sudo('cat {0}'
                               .format(daemon_path)).output
        daemon_as_json = json.loads(contents)
        process_management = daemon_as_json.pop('process_management')
        daemon = DaemonFactory._find_implementation(process_management)
        return daemon(
            **daemon_as_json
        )

    @staticmethod
    def save(daemon):
        runner = LocalCommandRunner(logger=api_logger)

        if not os.path.exists(CLOUDIFY_AGENT_STORAGE):
            runner.sudo('mkdir {0}'.format(CLOUDIFY_AGENT_STORAGE))

        daemon_path = os.path.join(
            CLOUDIFY_AGENT_STORAGE, '{0}.json'.format(daemon.name)
        )
        temp = tempfile.mkstemp()
        with open(temp[1], 'w') as f:
            props = {
                'name': daemon.name,
                'queue': daemon.queue,
                'manager_ip': daemon.manager_ip,
                'host': daemon.host,
                'user': daemon.user,
                'process_management': daemon.PROCESS_MANAGEMENT
            }
            props.update(**daemon.optional_parameters)
            json.dump(props, f, indent=2)
        runner.sudo('cp {0} {1}'.format(temp[1], daemon_path))

    @staticmethod
    def delete(daemon):
        daemon_context = os.path.join(CLOUDIFY_AGENT_STORAGE,
                                      '{0}.json'.format(daemon.name))
        runner = LocalCommandRunner(logger=api_logger)
        runner.sudo('rm {0}'.format(daemon_context))
