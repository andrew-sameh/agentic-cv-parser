import logging
import sys
import structlog
from structlog.types import EventDict, Processor



# https://github.com/hynek/structlog/issues/35#issuecomment-591321744
def rename_event_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Log entries keep the text message in the `event` field, but Datadog
    uses the `message` field. This processor moves the value from one field to
    the other.
    See https://github.com/hynek/structlog/issues/35#issuecomment-591321744
    """
    event_dict["message"] = event_dict.pop("event")
    return event_dict

def drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Uvicorn logs the message a second time in the extra `color_message`, but we don't
    need it. This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict

def configure_logger(log_level:str = "INFO", enable_json_logs: bool = False):
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

    shared_processors = [
        timestamper,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        # structlog.processors.CallsiteParameterAdder(
        #     {
        #         structlog.processors.CallsiteParameter.PATHNAME,
        #         structlog.processors.CallsiteParameter.FILENAME,
        #         structlog.processors.CallsiteParameter.MODULE,
        #         structlog.processors.CallsiteParameter.FUNC_NAME,
        #         structlog.processors.CallsiteParameter.THREAD,
        #         structlog.processors.CallsiteParameter.THREAD_NAME,
        #         structlog.processors.CallsiteParameter.PROCESS,
        #         structlog.processors.CallsiteParameter.PROCESS_NAME,
        #     }
        # ),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.StackInfoRenderer(),
        drop_color_message_key,

    ]

    if enable_json_logs:
        # We rename the `event` key to `message` only in JSON logs, as Datadog looks for the
        # `message` key but the pretty ConsoleRenderer looks for `event`
        shared_processors.append(rename_event_key)
        # Format the exception only for JSON logs, as we want to pretty-print them when
        # using the ConsoleRenderer
        shared_processors.append(structlog.processors.format_exc_info)
    else:
        shared_processors.append(structlog.processors.ExceptionPrettyPrinter())

    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        # call log with await syntax in thread pool executor
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        # wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logs_render = (
        structlog.processors.JSONRenderer()
        if enable_json_logs
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    _configure_default_logging_by_custom(shared_processors, logs_render, log_level)


def _configure_default_logging_by_custom(shared_processors, logs_render, log_level="INFO"):
    handler = logging.StreamHandler()

    # Use `ProcessorFormatter` to format all `logging` entries.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            # _extract_from_record,
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            logs_render,
        ],
    )

    handler.setFormatter(formatter)
    root_uvicorn_logger = logging.getLogger()
    root_uvicorn_logger.handlers.clear()
    root_uvicorn_logger.addHandler(handler)
    root_uvicorn_logger.setLevel(log_level.upper())

    # for _log in ["uvicorn", "uvicorn.error"]:
        # Clear the log handlers for uvicorn loggers, and enable propagation
        # so the messages are caught by our root logger and formatted correctly
        # by structlog
        # logging.getLogger(_log).handlers.clear()
        # logging.getLogger(_log).propagate = True

    # Since we re-create the access logs ourselves, to add all information
    # in the structured log (see the `logging_middleware` in main.py), we clear
    # the handlers and prevent the logs to propagate to a logger higher up in the
    # hierarchy (effectively rendering them silent).
    # logging.getLogger("uvicorn.access").handlers.clear()
    # logging.getLogger("uvicorn.access").propagate = False

    def handle_exception(exc_type, exc_value, exc_traceback):
        """
        Log any uncaught exception instead of letting it be printed by Python
        (but leave KeyboardInterrupt untouched to allow users to Ctrl+C to stop)
        See https://stackoverflow.com/a/16993115/3641865
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_uvicorn_logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception

def _extract_from_record(_, __, event_dict):
    # Extract thread and process names and add them to the event dict.
    record = event_dict["_record"]
    event_dict["thread_name"] = record.threadName
    event_dict["process_name"] = record.processName
    return event_dict