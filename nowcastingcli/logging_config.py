# nowcastingcli/logging_config.py
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {
            "format": "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",        # only warnings+ to terminal
            "formatter": "plain",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",          # everything to file
            "formatter": "json",
            "filename": "logs/nowcastingcli.log",
            "maxBytes": 1_000_000,
            "backupCount": 3,
        },
    },
    "loggers": {
        "nowcastingcli": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,        # don't double-log to root
        },
    },
}


def setup_logging() -> None:
    import os
    os.makedirs("logs", exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)