# import logging 
# logger=logging.getLogger("note_manager")
# logger.setLevel(logging.DEBUG)
# console_handler=logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)

# file_handler=logging.FileHandler("app.log")
# file_handler.setLevel(logging.INFO)
# formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# console_handler.setFormatter(formatter)
# file_handler.setFormatter(formatter)

# logger.addHandler(console_handler)
# logger.addHandler(file_handler)

import logging
import logging.config

logging_config={
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        },
        "simple": {
            "format": "%(levelname)s: %(message)s"
        },
        "simple":{
            "format":"%(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "level": "ERROR",
            "stream": "ext://sys.stderr",
            },},
    "root":{
        "handlers": ["stdout", "stderr"],
        "level": "DEBUG",},
    "loggers":{
        "app":{"handlers": ["stdout", "stderr"],
            "level": "INFO",
            "propagate": False,
    },},}

def setup_logging():
    logging.config.dictConfig(logging_config)

logger=logging.getLogger("app")