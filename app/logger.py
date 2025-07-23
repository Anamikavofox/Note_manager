import logging
import logging.config
import os 

log_dir="logs"
os.makedirs(log_dir,exist_ok=True)

logging_config={
    "version":1,
    "disable_existing_loggers": True,
    "formatters": {
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        },
        "simple": {
            "format": "%(levelname)s: %(message)s"
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
            },
        "file":{
            "class":"logging.FileHandler",
            "formatter":"detailed",
            "level":"INFO",
            "filename":os.path.join(log_dir,"app.log"),
            "mode":"a",
        },},
    "root":{
        "handlers": ["stdout", "stderr","file"],
        "level": "DEBUG",},
    "loggers":{
        "app":{
            "handlers": ["stdout", "stderr","file"],
            "level": "INFO",
            "propagate": False,
    },
    },
    }
def setup_logging():
    logging.config.dictConfig(logging_config)

logger=logging.getLogger("app")
