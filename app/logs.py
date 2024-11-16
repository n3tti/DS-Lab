import logging
import structlog
import sys

# logging.basicConfig(
#     stream=sys.stdout,
#     format="%(message)s",
#     level=logging.INFO,
# )

def uppercase_log_level(logger, log_method, event_dict):
    if 'level' in event_dict:
        event_dict['level'] = event_dict['level'].upper()
    return event_dict


shared_processors = [
    # Processors that have nothing to do with output,
    # e.g., add timestamps or log level names.
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.ExceptionPrettyPrinter(),
    structlog.processors.StackInfoRenderer(),
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

# # Configure structlog with advanced processors
# structlog.configure(
#     processors=processors,
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
#     cache_logger_on_first_use=True,
# )

# # Create a logger
# logger = structlog.get_logger()









# # import logging
# # import structlog
# # import sys
# import os

# JSON_LOGGING = os.getenv("JSON_LOGGING") == "true"


# def event_uppercase(logger, method_name, event_dict):  # type: ignore
#     event_dict["level"] = event_dict["level"].upper()
#     return event_dict


# foreign_pre_chain = [
#     structlog.contextvars.merge_contextvars,
#     # structlog.stdlib.filter_by_level,
#     structlog.stdlib.add_logger_name,
#     structlog.stdlib.add_log_level,
# ]

# shared_processors = [
#     structlog.contextvars.merge_contextvars,
#     # structlog.stdlib.filter_by_level,
#     structlog.stdlib.add_logger_name,
#     structlog.stdlib.add_log_level,
#     structlog.stdlib.PositionalArgumentsFormatter(),
#     structlog.processors.TimeStamper("%Y-%m-%d %H:%M:%S.%f"),
#     structlog.processors.StackInfoRenderer(),
#     structlog.processors.format_exc_info,
#     structlog.processors.UnicodeDecoder(),
# ]

# structlog.configure(
#     processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
#     context_class=structlog.threadlocal.wrap_dict(dict),
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.stdlib.BoundLogger,
#     cache_logger_on_first_use=True,
# )

# logging.config.dictConfig(
#     {
#         "version": 1,
#         "disable_existing_loggers": False,
#         "root": {
#             "level": "INFO",
#             "handlers": ["console"] if not JSON_LOGGING else ["json"],
#         },
#         "formatters": {
#             "json_formatter": {
#                 "()": structlog.stdlib.ProcessorFormatter,
#                 "processors": [
#                     event_uppercase,
#                     structlog.stdlib.ProcessorFormatter.remove_processors_meta,
#                     structlog.processors.EventRenamer("message"),
#                     structlog.processors.JSONRenderer(),
#                 ],
#                 "foreign_pre_chain": foreign_pre_chain,
#             },
#             "console_formatter": {
#                 "()": structlog.stdlib.ProcessorFormatter,
#                 "processor": structlog.dev.ConsoleRenderer(),
#                 "foreign_pre_chain": foreign_pre_chain,
#             },
#         },
#         "handlers": {
#             "json": {
#                 "class": "logging.StreamHandler",
#                 "formatter": "json_formatter",
#                 "stream": "ext://sys.stdout",
#             },
#             "console": {
#                 "class": "logging.StreamHandler",
#                 "formatter": "console_formatter",
#             },
#         },
#     }
# )


logger = structlog.get_logger()
