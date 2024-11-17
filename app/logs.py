import logging
import structlog
import sys

logging.basicConfig(
    stream=sys.stdout,
    format="%(message)s",
    level=logging.INFO,
)

def uppercase_log_level(logger, log_method, event_dict):
    if 'level' in event_dict:
        event_dict['level'] = event_dict['level'].upper()
    return event_dict


shared_processors = [
    # Processors that have nothing to do with output,
    # e.g., add timestamps or log level names.

    # structlog.stdlib.filter_by_level,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.ExceptionPrettyPrinter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.contextvars.merge_contextvars,
]

if sys.stderr.isatty():
    # Pretty printing when we run in a terminal session.
    # Automatically prints pretty tracebacks when "rich" is installed
    processors = shared_processors + [
        structlog.dev.ConsoleRenderer(),
    ]
else:
    # Print JSON when we run, e.g., in a Docker container.
    # Also print structured tracebacks.
    processors = shared_processors + [
        uppercase_log_level,
        structlog.processors.dict_tracebacks,
        structlog.processors.EventRenamer("message"),
        structlog.processors.JSONRenderer(),
    ]


##################################################
structlog.configure(
    processors=processors,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

#################################################


# Adapt logging to use the same config as structlog
formatter = structlog.stdlib.ProcessorFormatter(
    processors=processors,
)

handler = logging.StreamHandler()
# Use OUR `ProcessorFormatter` to format all `logging` entries.
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)


# logging.basicConfig(level=logging.ERROR, format='%(message)s')

##################################################

# structlog.configure(
#     wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
# )
##################################################





logger = structlog.get_logger()

# structlog.stdlib.filter_by_level(logger, "info", {})
