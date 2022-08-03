import os
import logging
import logging.handlers as handlers
from ulti import read_yaml

config_file = "/tools/HAService/config.yaml"
logging_folder = "/tools/HAService/logs"
logging_file = "current.log"

# Required global (config.yaml) configuration options
required_globals = frozenset(['service'])
required_services = frozenset(['name', 'paths', 'exclude', 'node_peer'])


def check_required(config):
    # Make sure we have all required globals
    if not required_globals.issubset(config.keys()):
        raise Exception('%s must contain %s' % (config_file, ', '.join(required_globals - frozenset(list(config.keys())))))
    # Make sure we have all required services
    if not required_services.issubset(config['service'].keys()):
        raise Exception('%s must contain %s' % (config_file, ', '.join(required_services - frozenset(list(config['service'].keys())))))


def load_config():
    config = read_yaml(config_file)
    check_required(config)
    return config


# Logging configuration
def load_logging():
    # Create logging folder if it doesn't exist
    if not os.path.exists(logging_folder):
        os.makedirs(logging_folder)
    # Create logging file if it doesn't exist
    file_path = logging_folder + '/' + logging_file
    if not os.path.exists(file_path):
        open(file_path, 'a').close()
    # Set logging configuration

    log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    logger = logging.getLogger('sync')
    logger.setLevel(logging.DEBUG)
    log_handler = handlers.TimedRotatingFileHandler(filename=file_path, when='d', interval=1, backupCount=7)
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    return logger
