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


def render_template_to_tempfile(template_path, **values):

    """
    Render a 'jinja' template resource to a temporary file.

    :param template_path: relative path to the template.
    :type template_path: str

    :param values: keyword arguments passed to jinja.
    :type values: dict

    :return path to the temporary file.
    :rtype `str`
    """

    template = get_resource(template_path)
    rendered = Template(template).render(**values)
    return content_to_tempfile(rendered)


def resource_to_tempfile(resource_path):

    """
    Copy a resource into a temporary file.

    :param resource_path: relative path to the resource.
    :type resource_path: str

    :return path to the temporary file.
    :rtype `str`
    """

    resource = get_resource(resource_path)
    return content_to_tempfile(resource)


def get_resource(resource_path):

    """
    Loads the resource into a string.

    :param resource_path: relative path to the resource.
    :type resource_path: str

    :return the resource as a string.
    :rtype `str`
    """

    return pkg_resources.resource_string(
        cloudify_agent.__name__,
        os.path.join('resources', resource_path)
    )


def content_to_tempfile(content):

    """
    Write string to a temporary file.

    :param content:
    :type content: str

    :return path to the temporary file.
    :rtype `str`
    """

    temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    with open(temp.name, 'r+') as f:
        f.write(content)
        f.write(os.linesep)
    path = temp.name
    return path
