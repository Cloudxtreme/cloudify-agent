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
import pkg_resources
from jinja2 import Template

import cloudify_agent


def rendered_template_to_tempfile(template_path, **values):
    template = get_resource(template_path)
    rendered = Template(template).render(**values)
    return content_to_tempfile(rendered)


def resource_to_tempfile(resource_path):
    resource = get_resource(resource_path)
    return content_to_tempfile(resource)


def get_resource(resource_path):
    return pkg_resources.resource_string(
        cloudify_agent.__name__,
        os.path.join('resources', resource_path)
    )


def content_to_tempfile(content):
    temp = tempfile.mkstemp()
    with open(temp[1], 'w') as f:
        f.write(content)
        return f.name


