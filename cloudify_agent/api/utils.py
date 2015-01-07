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
import tempfile
import json
from jinja2 import Template

CONTEXT_FOLDER_NAME = '.cloudify-agent'


def render_template(template, **values):
    template = Template(template)
    rendered = template.render(**values)
    temp = tempfile.mkstemp()
    with open(temp[1], 'w') as f:
        f.write(rendered)
        f.write(os.linesep)
        return f.name


def load_daemon_context(queue):
    context_path = os.path.join(os.getcwd(), CONTEXT_FOLDER_NAME,
                                '{0}.json'.format(queue))
    if not os.path.exists(context_path):
        raise RuntimeError('Cannot load daemon context: {0} does not exists. '
                           'Are you sure you are in the correct directory?'
                           .format(queue))
    return json.load(open(context_path))


def dump_daemon_context(queue, context):

    context_folder = os.path.join(os.getcwd(), CONTEXT_FOLDER_NAME)
    context_path = os.path.join(context_folder,
                                '{0}.json'.format(queue))
    if not os.path.exists(context_folder):
        os.makedirs(context_folder)

    with open(context_path, 'w') as outfile:
        json.dump(context, outfile)
