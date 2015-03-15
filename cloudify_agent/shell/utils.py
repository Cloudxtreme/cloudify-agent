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

from cloudify_agent.api import utils as api_utils


def initialize(logfile=None):

    """
    initializes cloudify-agent in the current working directory. All this
    function actually does is create the logging.yaml configuration file.
    if the directory is already initialized, this function does nothing.

    :param logfile: path to a file where all cloudify-agent logs will be
    stored. if none is specified the following path will be used:
    <workdir>/.cloudify-agent/cloudify-agent.log
    :type logfile: str

    """

    init_directory = get_init_directory()
    if os.path.exists(init_directory):
        return
    os.makedirs(init_directory)
    if not logfile:
        logfile = os.path.join(init_directory, 'cloudify-agent.log')
    api_utils.render_template_to_file(
        'shell/logging.yaml',
        file_path=os.path.join(init_directory, 'logging.yaml'),
        logfile=logfile)


def is_initialized():

    """
    checks if the current working directory is initialized.

    :return: whether or not the directory is initialized.
    :rtype `bool`
    """
    return os.path.exists(get_init_directory())


def get_init_directory():

    """
    retrieves the inner cloudify-agent directory from the current working
    directory.

    :return: path to the initialization directory.
    :rtype `str`

    """

    workdir = os.getcwd()
    return os.path.join(
        workdir, '.cloudify-agent'
    )


def get_storage_directory():
    return os.path.join(
        get_init_directory(), 'daemons'
    )


def show_possible_solutions(failure):

    def recommend(possible_solutions):
        failure_message = 'Possible solutions'
        for solution in possible_solutions:
            failure_message = '  - {0}{1}'.format(solution, os.linesep)
        return failure_message

    if hasattr(failure, 'possible_solutions'):
        return recommend(getattr(failure, 'possible_solutions'))
    else:
        return ''


def setup_loggers(debug):
    pass