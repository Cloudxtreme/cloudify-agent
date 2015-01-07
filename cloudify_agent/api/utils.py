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

from cloudify.utils import LocalCommandRunner


def extract_module_paths_from_name(virtualenv_path, plugin_name):
    module_paths = []
    runner = LocalCommandRunner()
    files = runner.run(
        '{0}/bin/pip show -f {1}'
        .format(virtualenv_path, plugin_name)
    ).std_out.splitlines()
    for module in files:
        if module.endswith('.py') and '__init__' not in module:
            # the files paths are relative to the package __init__.py file.
            module_paths.append(module.replace('../', '')
                                .replace('/', '.').replace('.py', '').strip())
    return module_paths
