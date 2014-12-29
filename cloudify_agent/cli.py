import argparse


def run(cmd, no_print=False):
    """executes a command

    :param string cmd: command to execute
    """
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    if not no_print:
        if len(stdout) > 0:
            lgr.debug('stdout: {0}'.format(stdout))
        if len(stderr) > 0:
            lgr.debug('stderr: {0}'.format(stderr))
    p.stdout = stdout
    p.strerr = stderr
    return p


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--virtual-env', required=True)
    parser.add_argument('--broker-url', required=True)
    parser.add_argument('--install', required=False)
    return parser.parse_args()


def set_env():
    # os.environ['BROKER_IP'] =
    # os.environ['MANAGEMENT_IP'] =
    # os.environ['BROKER_URL'] =
    # os.environ['MANAGER_REST_PORT'] =
    # os.environ['CELERY_WORK_DIR'] =
    # os.environ['IS_MANAGEMENT_NODE'] =
    # os.environ['AGENT_IP'] =
    # os.environ['VIRTUALENV'] =
    # os.environ['MANAGER_FILE_SERVER_URL'] =
    # os.environ['MANAGER_FILE_SERVER_BLUEPRINTS_ROOT_URL'] =
    # os.environ['PATH'] =
    run('x')

def main():
    args = parse_args()
    run('{0}/env/bin/python -m celery.bin.celeryd ')


# resources management
# if system == ubuntu and procman == sysv:
#   move resources/sysv /etc/init.d
# elif system == redhat and procman == sysv:
#   move resources/sysv /etc/rc.d/init.d
# elif system == ubuntu and procman == upstart:
#   move resources/upstart /etc/init





# . {{ includes_file_path }}
# CELERY_BASE_DIR="{{ celery_base_dir }}"

# # replaces management__worker
# WORKER_MODIFIER="{{ worker_modifier }}"

# export BROKER_IP="{{ broker_ip }}"
# export MANAGEMENT_IP="{{ management_ip }}"
# export BROKER_URL="amqp://guest:guest@${BROKER_IP}:5672//"
# export MANAGER_REST_PORT="80"
# export CELERY_WORK_DIR="${CELERY_BASE_DIR}/cloudify.${WORKER_MODIFIER}/work"
# export IS_MANAGEMENT_NODE="False"
# export AGENT_IP="{{ agent_ip }}"
# export VIRTUALENV="${CELERY_BASE_DIR}/cloudify.${WORKER_MODIFIER}/env"
# export MANAGER_FILE_SERVER_URL="http://${MANAGEMENT_IP}:53229"
# export MANAGER_FILE_SERVER_BLUEPRINTS_ROOT_URL="${MANAGER_FILE_SERVER_URL}/blueprints"
# export PATH="${VIRTUALENV}/bin:${PATH}"

# CELERYD_MULTI="${VIRTUALENV}/bin/celeryd-multi"
# CELERYD_USER="{{ celery_user }}"
# CELERYD_GROUP="{{ celery_group }}"
# CELERY_TASK_SERIALIZER="json"
# CELERY_RESULT_SERIALIZER="json"
# CELERY_RESULT_BACKEND="$BROKER_URL"
# DEFAULT_PID_FILE="${CELERY_WORK_DIR}/celery.pid"
# DEFAULT_LOG_FILE="${CELERY_WORK_DIR}/celery.log"
# CELERYD_OPTS="--events --loglevel=debug --app=cloudify --include=${INCLUDES} -Q ${WORKER_MODIFIER} --broker=${BROKER_URL} --hostname=${WORKER_MODIFIER} --autoscale={{ worker_autoscale }} --maxtasksperchild=10"
