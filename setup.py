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


from setuptools import setup

install_requires = [
    'cloudify-plugins-common==3.2a1',
    'cloudify-rest-client==3.2a1',
    'cloudify-script-plugin==1.2a1',
    'cloudify-diamond-plugin==1.2a1',
    'cloudify-agent-installer-plugin==1.2a1',
    'cloudify-plugin-installer-plugin==1.2a1',
    'cloudify-windows-agent-installer-plugin==1.2a1',
    'cloudify-windows-plugin-installer-plugin==1.2a1',
    'click==3.3',
    'celery==3.0.24',
    'jinja2==2.7.2'
]

try:
    import argparse  # NOQA
except ImportError, e:
    install_requires.append('argparse==1.2.2')

setup(
    name='cloudify-agent',
    version='3.2a1',
    author='Gigaspaces',
    author_email='cloudify@gigaspaces.com',
    packages=[
        'cloudify_agent',
        'cloudify_agent.api',
        'cloudify_agent.api.internal',
        'cloudify_agent.api.internal.daemon',
        'cloudify_agent.shell',
        'cloudify_agent.shell.subcommands'
    ],
    package_data={
        'cloudify_agent': [
            'resources/celeryd.conf.template',
            'resources/celeryd.template',
            'resources/disable-requiretty.sh'],
        },
    description="Cloudify's Agent",
    install_requires=install_requires,
    license='LICENSE',
    entry_points={
        'console_scripts': [
            'cloudify-agent = cloudify_agent.shell.cli:main',
        ]
    }
)
