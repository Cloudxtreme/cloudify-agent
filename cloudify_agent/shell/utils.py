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
import logging
import yaml

from cloudify_agent.api import utils as api_utils
from cloudify_agent import dictconfig


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

    if is_initialized():
        return
    init_directory = get_init_directory()
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


def get_possible_solutions(failure):

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
    initialize()
    config_path = os.path.join(get_init_directory(), 'logging.yaml')
    logging_config = yaml.safe_load(file(config_path, 'r'))['logging']
    loggers_config = logging_config['loggers']
    logfile = logging_config['filename']
    logfile_format = logging_config['file_format']
    log_format = logging_config['format']

    handlers = {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'file',
            'maxBytes': '5000000',
            'backupCount': '20',
            'filename': logfile
        },
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'console'
        }
    }

    formatters = {
        'file': {
            'format': logfile_format
        },
        'console': {
            'format': log_format
        }
    }

    logger_dict = {
        'version': 1,
        'handlers': handlers,
        'formatters': formatters
    }

    # add handlers to every logger specified in the file
    loggers = {}
    for logger_name in loggers_config:
        loggers[logger_name] = {
            'handlers': list(handlers.keys())
        }
    logger_dict['loggers'] = loggers

    # set level for each logger
    for logger_name, logging_level in loggers_config.iteritems():
        log = logging.getLogger(logger_name)
        level = logging._levelNames[
            logging.DEBUG if debug else logging_level.upper()]
        log.setLevel(level)

    dictconfig.dictConfig(logger_dict)
