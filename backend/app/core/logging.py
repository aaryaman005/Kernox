import logging
import sys

from app.core.request_context import request_id_ctx_var


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get()
        return True


def configure_logging():
    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | request_id=%(request_id)s | %(message)s"
    )

    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addFilter(RequestIDFilter())
