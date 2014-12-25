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
    'cloudify-script-plugin==1.1a2',
    'cloudify-diamond-plugin==1.1a2',
    # 'cloudify-agent-installer==1.1a2',
    # 'cloudify-plugin-installer==1.1a2',
    # 'cloudify-windows-agent-installer==1.1a2',
    # 'cloudify-windows-plugin-installer==1.1a2',
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
    packages=['cloudify_agent'],
    description='Cloudify\'s Agent',
    install_requires=install_requires,
    license='LICENSE',
    # entry_points={
    #     'console_scripts': [
    #         'cfy-agent = cloudify_agent.cli:main',
    #     ]
    # }
)
