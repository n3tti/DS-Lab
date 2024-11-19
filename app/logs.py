import logging
import sys

import structlog

from app.config import DEBUG, LOG_LEVEL


def get_lower_log_level(current_level):
    lower_level = max(current_level - 10, logging.NOTSET)  # ensure it does not go below NOTSET
    return lower_level


# Disabling logs until LOG_LEVEL so that scrapy doesn't override
logging.disable(get_lower_log_level(LOG_LEVEL))


def uppercase_log_level(logger, log_method, event_dict):
    if "level" in event_dict:
        event_dict["level"] = event_dict["level"].upper()
    return event_dict


def colorize_log_level(logger, method_name, event_dict):
    level = event_dict.get("level", "").lower()
    colors = {"debug": "\033[32m", "info": "\033[1;32m", "warning": "\033[33m", "error": "\033[91m", "critical": "\033[31m"}
    reset_color = "\033[0m"
    if level in colors:
        event_dict["level"] = f"{colors[level]}{level.upper()}{reset_color}"

    return event_dict


shared_processors = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.ExceptionPrettyPrinter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.contextvars.merge_contextvars,
    structlog.processors.UnicodeDecoder(),
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.PATHNAME,
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO,
        }
    ),
]

if sys.stderr.isatty():
    processors = shared_processors + [colorize_log_level]
    rendering_processor = structlog.dev.ConsoleRenderer()
else:
    processors = shared_processors + [
        structlog.processors.dict_tracebacks,
        structlog.processors.EventRenamer("message"),
        uppercase_log_level,
    ]
    rendering_processor = structlog.processors.JSONRenderer()


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        *processors,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
# #################################################


# Adapt logging to use the same configuration as structlog
formatter = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=processors,
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        rendering_processor,
    ],
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(LOG_LEVEL)


logger = structlog.get_logger()
