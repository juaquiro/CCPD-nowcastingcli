# nowcastingcli/logging_config.py
import logging.config

# Schema consumed by logging.config.dictConfig() — see the stdlib "dictionary
# schema" docs. Structure:
#   version: must be 1 (only schema version defined by the stdlib).
#   disable_existing_loggers: False, so loggers created via getLogger() before
#     this config runs are kept instead of being silenced.
#   formatters: name -> formatter spec.
#     "()" is a special key: a dotted path to a callable/class to instantiate
#     in place of the default logging.Formatter (used here for JsonFormatter).
#   handlers: name -> handler spec.
#     "class" is a dotted path to the handler class; all other keys are
#     passed through as constructor kwargs. "formatter" references a key in
#     formatters. "ext://..." resolves a dotted path to an existing object
#     (e.g. sys.stderr) rather than instantiating one.
#   loggers: name -> logger spec.
#     "handlers" is a list of handler names above. "propagate": False stops
#     records from bubbling up to the root logger. Child loggers created via
#     getLogger(__name__) (e.g. "nowcastingcli.physics") inherit this config
#     through the dotted-name hierarchy without their own entry.
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