from file_handler import FileHandler
from service_handler import ServiceHandler
from loader import load_config
from loader import load_logging
from killer import GracefulKiller


conf = load_config()
logger = load_logging()
logger.info("Logging configuration loaded")
logger.info("Service name: " + conf['service']['name'])
for path in conf['service']['paths']:
    logger.info("Sync path: " + path)
for path in conf['service']['exclude']:
    logger.info("Exclude path: " + path)
logger.info("Remote server: " + conf['service']['node_peer'])


if __name__ == "__main__":
    service = conf['service']
    files_handler = FileHandler(service)
    files_handler.start()

    service_handler = ServiceHandler(service['name'])
    service_handler.start()
    logger.info("Service handler started")

    killer = GracefulKiller()
    while not killer.kill_now:
        if service_handler.is_changed:
            logger.info("Service {service_name} state changed".format(service_name=service['name']))
            service_handler.is_changed = False
            # Validates the local configuration file
            if service_handler.validate_config():
                logger.info("Local service {service_name} configuration is valid".format(service_name=service['name']))
                # Validates the remote configuration file
                if service_handler.remote_validate_config(conf['service']['node_peer']):
                    logger.info("Remote service {service_name} configuration is valid".format(service_name=service['name']))
                    # Restarts the service if the configuration is valid
                    if service_handler.remote_reload_service(conf['service']['node_peer']):
                        logger.info("Remote service {service_name} restarted".format(service_name=service['name']))
                    else:
                        logger.error("Remote service {service_name} restart failed".format(service_name=service['name']))
                else:
                    logger.error("Remote service {service_name} configuration is invalid".format(service_name=service['name']))
            else:
                logger.error("Local service {service_name} configuration is invalid".format(service_name=service['name']))
