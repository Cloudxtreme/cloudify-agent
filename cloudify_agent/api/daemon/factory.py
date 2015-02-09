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
from cloudify_agent.api.daemon.base import Daemon
from cloudify_agent.api import api_logger
from cloudify_agent.api import utils
from cloudify_agent import VIRTUALENV
from cloudify_agent import CLOUDIFY_AGENT_STORAGE


class DaemonFactory(object):

    """
    Factory class for manipulating various daemon instances.

    """

    @staticmethod
    def _find_implementation(process_management):

        """
        Locates the proper daemon implementation for the specific
        process management system. For this to work, all implementations
        need to be imported at this time.

        see api/internal/daemon/__init__.py

        :param process_management: The process management type.
        :type process_management: str

        :raise RuntimeError: if no implementation could be found.
        """

        daemons = Daemon.__subclasses__()
        for daemon in daemons:
            if daemon.PROCESS_MANAGEMENT == process_management:
                return daemon
        raise RuntimeError('No implementation found for daemon of type: {0}'
                           .format(process_management))

    @staticmethod
    def _disable_requiretty():

        """
        Disables the requiretty directive in the /etc/sudoers file. This
        will enable operations that require sudo permissions to work properly.

        This is needed because operations are executed
        from within the worker process, which is not a tty process.

        """

        runner = LocalCommandRunner()

        disable_requiretty_script_path = utils.resource_to_tempfile(
            resource_path='disable-requiretty.sh'
        )
        runner.run('chmod +x {0}'.format(disable_requiretty_script_path))
        runner.sudo('{0}'.format(disable_requiretty_script_path))

    @staticmethod
    def _fix_env():

        """
        This method is used for auto-configuration of the virtualenv.
        It is needed in case the environment was created using different paths
        than the one that is used at runtime.

        """

        bin_dir = '{0}/bin'.format(VIRTUALENV)

        for executable in os.listdir(bin_dir):
            path = os.path.join(bin_dir, executable)
            if not os.path.isfile(path):
                continue
            if os.path.islink(path):
                continue
            basename = os.path.basename(path)
            if basename in ['python', 'python2.7', 'python2.6']:
                continue
            with open(path) as f:
                lines = f.read().split(os.linesep)
                if lines[0].endswith('/bin/python'):
                    lines[0] = '#!{0}/python'.format(bin_dir)
            with open(path, 'w') as f:
                f.write(os.linesep.join(lines))

        runner = LocalCommandRunner()

        for link in ['archives', 'bin', 'include', 'lib']:
            link_path = '{0}/local/{1}'.format(VIRTUALENV, link)
            try:
                runner.run('unlink {0}'.format(link_path))
                runner.run('ln -s {0}/{1} {2}'
                           .format(VIRTUALENV, link, link_path))
            except CommandExecutionException:
                pass

    @staticmethod
    def new(process_management, **params):

        """
        Creates a daemon instance that implements the required process
        management.

        :param process_management: The process management to use.
        :type process_management: str

        :param params: parameters passed to the daemon class constructor.
        :type params: dict

        :return: A daemon instance.
        :rtype `cloudify_agent.api.internal.daemon.base.Daemon`
        """

        daemon = DaemonFactory._find_implementation(process_management)
        instance = daemon(**params)
        if instance.relocated:
            DaemonFactory._fix_env()
        if instance.disable_requiretty:
            DaemonFactory._disable_requiretty()
        return instance

    @staticmethod
    def load(name):

        """
        Loads a daemon from local storage.

        :param name: The name of the daemon to load.
        :type name: str

        :return: A daemon instance.
        :rtype `cloudify_agent.api.internal.daemon.base.Daemon`

        :raise IOError: in case the daemon file does not exist.
        """

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

        """
        Saves a daemon to the local storage. The daemon is stored in json
        format and contains all daemon properties.

        :param daemon: The daemon instance to save.
        :type daemon: `cloudify_agent.api.internal.daemon.base.Daemon`
        """

        runner = LocalCommandRunner(logger=api_logger)

        if not os.path.exists(CLOUDIFY_AGENT_STORAGE):
            runner.sudo('mkdir -p {0}'.format(CLOUDIFY_AGENT_STORAGE))

        daemon_path = os.path.join(
            CLOUDIFY_AGENT_STORAGE, '{0}.json'.format(daemon.name)
        )
        temp = tempfile.mkstemp()
        with open(temp[1], 'w') as f:
            props = daemon.__dict__
            # remove non-serializable objects
            props.pop('runner')
            props.pop('logger')
            props.pop('celery')
            json.dump(props, f, indent=2)
            f.write(os.linesep)
        runner.sudo('cp {0} {1}'.format(temp[1], daemon_path))
        runner.sudo('rm {0}'.format(temp[1]))

    @staticmethod
    def delete(name):

        """
        Deletes a daemon from local storage.

        :param name: The name of the daemon to delete.
        :type name: str
        """
        daemon_context = os.path.join(CLOUDIFY_AGENT_STORAGE,
                                      '{0}.json'.format(name))
        runner = LocalCommandRunner(logger=api_logger)
        runner.sudo('rm {0}'.format(daemon_context))
