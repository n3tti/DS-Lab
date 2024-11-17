import logging
import structlog
import sys


import logging
import structlog



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
    shared_processors = shared_processors
    rendering_processor = structlog.dev.ConsoleRenderer()
else:
    shared_processors = shared_processors + [
        uppercase_log_level,
        structlog.processors.dict_tracebacks,
        structlog.processors.EventRenamer("message"),
    ]
    rendering_processor = structlog.processors.JSONRenderer()



structlog.configure(
    processors=[
        # Prepare event dict for `ProcessorFormatter`.
        *shared_processors,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

formatter = structlog.stdlib.ProcessorFormatter(
    foreign_pre_chain=shared_processors,
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer(),
    ],
)

handler = logging.StreamHandler()
# Use OUR `ProcessorFormatter` to format all `logging` entries.
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)


# logging.basicConfig(
#     stream=sys.stdout,
#     format="%(message)s",
#     level=logging.INFO,
# )
# logging.disable(logging.DEBUG)

# def uppercase_log_level(logger, log_method, event_dict):
#     if 'level' in event_dict:
#         event_dict['level'] = event_dict['level'].upper()
#     return event_dict


# shared_processors = [
#     # Processors that have nothing to do with output,
#     # e.g., add timestamps or log level names.

#     # structlog.stdlib.filter_by_level,
#     structlog.stdlib.add_log_level,
#     structlog.stdlib.add_logger_name,
#     structlog.processors.TimeStamper(fmt="iso"),
#     structlog.processors.ExceptionPrettyPrinter(),
#     structlog.processors.StackInfoRenderer(),
#     structlog.processors.format_exc_info,
#     structlog.contextvars.merge_contextvars,
# ]

# if sys.stderr.isatty():
#     processors = shared_processors
#     rendering_processor = structlog.dev.ConsoleRenderer()
# else:
#     processors = shared_processors + [
#         uppercase_log_level,
#         structlog.processors.dict_tracebacks,
#         structlog.processors.EventRenamer("message"),
#     ]
#     rendering_processor = structlog.processors.JSONRenderer()


# # ##################################################
# structlog.configure(
#     processors=[
#         # structlog.stdlib.filter_by_level,
#         *processors,
#         rendering_processor,
#         # structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
#     ],
#     context_class=dict,
#     logger_factory=structlog.stdlib.LoggerFactory(),
#     wrapper_class=structlog.stdlib.BoundLogger,
#     cache_logger_on_first_use=True,
# )

# # #################################################


# # Adapt logging to use the same configuration as structlog

# # formatter = structlog.stdlib.ProcessorFormatter(
# #     # These run ONLY on `logging` entries that do NOT originate within
# #     # structlog.
# #     foreign_pre_chain=shared_processors,
# #     # These run on ALL entries after the pre_chain is done.
# #     processors=[
# #         # Remove _record & _from_structlog.
# #         structlog.stdlib.ProcessorFormatter.remove_processors_meta,
# #         structlog.dev.ConsoleRenderer(),
# #     ],
# # )

# formatter = structlog.stdlib.ProcessorFormatter(
#     foreign_pre_chain=processors,
#     processors=[
#         structlog.stdlib.ProcessorFormatter.remove_processors_meta,
#         rendering_processor,
#     ],
# )

# handler = logging.StreamHandler()
# # Use OUR `ProcessorFormatter` to format all `logging` entries.
# handler.setFormatter(formatter)
# root_logger = logging.getLogger()
# if (root_logger.hasHandlers()):
#     root_logger.handlers.clear()
# root_logger.addHandler(handler)
# # root_logger.setLevel(logging.INFO)
# # root_logger.propagate = False


# # # logging.basicConfig(level=logging.ERROR, format='%(message)s')

# # ##################################################

# # # structlog.configure(
# # #     wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
# # # )
# # ##################################################





logger = structlog.get_logger()

# structlog.stdlib.filter_by_level(logger, "info", {})
