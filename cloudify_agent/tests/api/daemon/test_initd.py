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

import uuid
import os

from cloudify_agent.api.daemon.initd import GenericLinuxDaemon
from cloudify_agent import VIRTUALENV
from cloudify_agent.tests import resources
from cloudify_agent.tests.api.daemon import BaseDaemonLiveTestCase
from cloudify_agent.tests.api.daemon import SudoLessLocalCommandRunner
from cloudify_agent.tests.api.daemon import patch_unless_travis
from cloudify_agent.tests.api.daemon import travis


def _sudoless_start_command(daemon):
    return '{0} start'.format(daemon.script_path)


def _sudoless_stop_command(daemon):
    return '{0} stop'.format(daemon.script_path)


SCRIPT_DIR = '/tmp/etc/init.d'
CONFIG_DIR = '/tmp/etc/default'


@patch_unless_travis(
    'cloudify_agent.api.daemon.base.LocalCommandRunner',
    SudoLessLocalCommandRunner)
@patch_unless_travis(
    'cloudify_agent.api.daemon.initd.GenericLinuxDaemon.SCRIPT_DIR',
    SCRIPT_DIR)
@patch_unless_travis(
    'cloudify_agent.api.daemon.initd.GenericLinuxDaemon.CONFIG_DIR',
    CONFIG_DIR)
@patch_unless_travis(
    'cloudify_agent.api.daemon.initd.start_command',
    _sudoless_start_command)
@patch_unless_travis(
    'cloudify_agent.api.daemon.initd.stop_command',
    _sudoless_stop_command)
class TestGenericLinuxDaemon(BaseDaemonLiveTestCase):

    def setUp(self):
        super(TestGenericLinuxDaemon, self).setUp()
        self.name = 'cloudify-agent-{0}'.format(str(uuid.uuid4())[0:4])
        self.queue = '{0}-queue'.format(self.name)
        self._smakedirs(CONFIG_DIR)
        self._smakedirs(SCRIPT_DIR)

    PROCESS_MANAGEMENT = 'init.d'

    def test_configure_disable_requiretty(self):
        if not travis():
            raise RuntimeError('Error! This test cannot be executed '
                               'outside of the travis CI '
                               'system since it may corrupt '
                               'your local system files')
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder,
            disable_requiretty=True
        )
        daemon.configure()
        self.runner.run('{0}/bin/pip install {1}/mock-plugin-sudo'
                        .format(VIRTUALENV,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        try:
            daemon.register('mock-plugin-sudo')
            daemon.start()
            sudo_test_file = os.path.join(self.temp_folder, 'sudo-test')
            task_name = 'mock_plugin_sudo.tasks.run'
            args = [sudo_test_file]
            async = self.celery.send_task(
                name=task_name,
                queue=self.queue,
                args=args)
            async.get(timeout=5)
            self.assertTrue(os.path.exists(sudo_test_file))
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin-sudo'
                            .format(VIRTUALENV),
                            stdout_pipe=False)

    def test_configure(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        self.assertTrue(os.path.exists(daemon.script_path))
        self.assertTrue(os.path.exists(daemon.config_path))
        self.assertTrue(os.path.exists(daemon.includes_file_path))

    def test_delete(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        daemon.start()
        daemon.stop()
        daemon.delete()
        self.assertFalse(os.path.exists(daemon.script_path))
        self.assertFalse(os.path.exists(daemon.config_path))
        self.assertFalse(os.path.exists(daemon.includes_file_path))

    def test_start(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        daemon.start()
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)

    def test_stop(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        daemon.start()
        daemon.stop()
        self.assert_daemon_dead(self.queue)

    def test_register(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        self.runner.run('{0}/bin/pip install {1}/mock-plugin'
                        .format(VIRTUALENV,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        try:
            daemon.register('mock-plugin')
            daemon.start()
            self.assert_registered_tasks(
                self.queue,
                additional_tasks=set(['mock_plugin.tasks.run'])
            )
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin'
                            .format(VIRTUALENV),
                            stdout_pipe=False)

    def test_restart(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        from cloudify_agent.tests import resources
        self.runner.run('{0}/bin/pip install {1}/mock-plugin'
                        .format(VIRTUALENV,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        daemon.start()
        try:
            daemon.register('mock-plugin')
            daemon.restart()
            self.assert_registered_tasks(
                self.queue,
                additional_tasks=set(['mock_plugin.tasks.run'])
            )
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin'
                            .format(VIRTUALENV),
                            stdout_pipe=False)

    def test_configure_twice(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        self.assertRaises(RuntimeError, daemon.configure)

    def test_configure_twice_only_script_path_exists(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()

        # delete includes and config files
        self.runner.sudo('rm {0}'.format(daemon.includes_file_path))
        self.runner.sudo('rm {0}'.format(daemon.config_path))

        self.assertRaises(RuntimeError, daemon.configure)

    def test_configure_twice_only_config_path_exists(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()

        # delete includes and script files
        self.runner.sudo('rm {0}'.format(daemon.includes_file_path))
        self.runner.sudo('rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon.configure)

    def test_configure_twice_only_includes_path_exists(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()

        # delete config and script files
        self.runner.sudo('rm {0}'.format(daemon.config_path))
        self.runner.sudo('rm {0}'.format(daemon.script_path))

        self.assertRaises(RuntimeError, daemon.configure)

    def test_start_with_error(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        self.runner.run('{0}/bin/pip install {1}/mock-plugin-error'
                        .format(VIRTUALENV,
                                os.path.dirname(resources.__file__)),
                        stdout_pipe=False)
        try:
            daemon.register('mock-plugin-error')
            try:
                daemon.start(timeout=5)
                self.fail('Expected start operation to fail '
                          'due to bad import')
            except RuntimeError as e:
                self.assertTrue('cannot import name non_existent' in str(e))
        finally:
            self.runner.run('{0}/bin/pip uninstall -y mock-plugin-error'
                            .format(VIRTUALENV),
                            stdout_pipe=False)

    def test_start_short_timeout(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        try:
            daemon.start(timeout=-1)
        except RuntimeError as e:
            self.assertTrue('waited for -1 seconds' in str(e))

    def test_start_twice(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        daemon.start()
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)
        daemon.start()
        self.assert_daemon_alive(self.queue)
        self.assert_registered_tasks(daemon.queue)

    def test_stop_short_timeout(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        daemon.start()
        try:
            daemon.stop(timeout=-1)
        except RuntimeError as e:
            self.assertTrue('waited for -1 seconds' in str(e))

    def test_stop_twice(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        daemon.start()
        daemon.stop()
        self.assert_daemon_dead(self.queue)
        daemon.stop()
        self.assert_daemon_dead(self.queue)

    def test_two_daemons(self):
        queue1 = '{0}-1'.format(self.queue)
        name1 = '{0}-1'.format(self.name)
        daemon1 = GenericLinuxDaemon(
            name=name1,
            queue=queue1,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon1.configure()

        daemon1.start()
        self.assert_daemon_alive(queue1)
        self.assert_registered_tasks(queue1)

        queue2 = '{0}-2'.format(self.queue)
        name2 = '{0}-2'.format(self.name)
        daemon2 = GenericLinuxDaemon(
            name=name2,
            queue=queue2,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon2.configure()

        daemon2.start()
        self.assert_daemon_alive(queue2)
        self.assert_registered_tasks(queue2)

    def test_delete_before_stop(self):
        daemon = GenericLinuxDaemon(
            name=self.name,
            queue=self.queue,
            host='127.0.0.1',
            manager_ip='127.0.0.1',
            user=self.username,
            workdir=self.temp_folder
        )
        daemon.configure()
        daemon.start()
        self.assertRaises(RuntimeError, daemon.delete)
