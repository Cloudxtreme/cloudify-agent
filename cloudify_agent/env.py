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
import os
import subprocess
import os
from cloudify.utils import LocalCommandRunner


def create_env(user,
               broker_ip,
               agent_ip,
               worker_modifier,
               worker_auto_scale):

    virtualenv_path = os.path.dirname(os.path.dirname(sys.executable))
    work_dir = os.path.join(os.path.dirname(virtualenv_path), 'work')
    celeryd_opts = [
        '--events',
        '--loglevel=debug',
        '--app=cloudify',
        '--include={0}'.format(_build_includes()),
        '-Q {0}'.format(worker_modifier),
        '--broker=amqp://guest:guest@{0}:5672//'.format(broker_ip),
        '--hostname={0}'.format(worker_modifier),
        '--autoscale={0}'.format(worker_auto_scale),
        '--maxtasksperchild=10'
    ]

    full_env = {}

    system_env = {
        'PATH': '${VIRTUALENV}/bin:${PATH}'.format(virtualenv_path)
    }

    cloudify_env = {
        'BROKER_IP': broker_ip,
        'MANAGEMENT_IP': broker_ip,
        'BROKER_URL': 'amqp://guest:guest@{0}:5672//'.format(broker_ip),
        'MANAGER_REST_PORT': 80,
        'CELERY_WORK_DIR': work_dir,
        'IS_MANAGEMENT_NODE': False,
        'AGENT_IP': agent_ip,
        'VIRTUALENV': virtualenv_path,
        'MANAGER_FILE_SERVER_URL': 'http://{0}:53229'.format(broker_ip),
        'MANAGER_FILE_SERVER_BLUEPRINTS_ROOT_URL': 'http://{0}:53229/blueprints'.format(broker_ip)
    }

    celery_env = {
        'CELERYD_USER': user,
        'CELERYD_GROUP': user,
        'CELERY_TASK_SERIALIZER': 'json',
        'CELERY_RESULT_SERIALIZER': 'json',
        'CELERYD_MULTI': '{0}/bin/celeryd-multi'.format(virtualenv_path),
        'DEFAULT_PID_FILE': '{0}/celery.pid'.format(work_dir),
        'DEFAULT_LOG_FILE': '{0}/celery.log'.format(work_dir),
        'CELERYD_OPTS': ' '.join(celeryd_opts)
    }

    full_env.update(system_env)
    full_env.update(cloudify_env)
    full_env.update(celery_env)

    return full_env


def _build_includes():

    p = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    module_names = map(lambda x: x.split('==')[0], out.split(os.linesep))
    includes = []
    for module_name in module_names:
        if module_name.startswith('cloudify-') \
                and module_name.endswith('-plugin'):
            from plugin_installer.tasks import extract_module_paths_from_name
            module_paths = extract_module_paths_from_name(module_name)
            includes.extend(module_paths)
    print includes

# out = LocalCommandRunner().run('pip list').std_out

os.system('pip list')
# p = subprocess.Popen(['pip', 'list'], stdout=subprocess.PIPE)
# out1, err = p.communicate()
# print out1

# module_names = map(lambda x: x.split(' ')[0], out.split(os.linesep))
# includes = []
# for module_name in module_names:
#     if module_name.startswith('cloudify-') \
#             and module_name.endswith('-plugin'):
#         from plugin_installer.tasks import extract_module_paths_from_name
#         module_paths = extract_module_paths_from_name(module_name)
#         includes.extend(module_paths)
# print includes