import json
import sys
from datetime import UTC, datetime

from asgi_correlation_id.context import correlation_id
from loguru import logger


def _inject_request_id(record: dict) -> None:
    """Pulls the current request's correlation ID into every log record automatically,
    so call sites never need to pass it explicitly."""
    record["extra"].setdefault("request_id", correlation_id.get() or "-")


def _json_sink(message) -> None:
    """Flat JSON-Lines output (one JSON object per line) — the shape log aggregators
    like CloudWatch/ELK expect, rather than loguru's default nested serialize=True."""
    record = message.record
    payload = {
        "timestamp": datetime.fromtimestamp(record["time"].timestamp(), tz=UTC).isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "logger": record["name"],
        "function": record["function"],
        "line": record["line"],
        **record["extra"],
    }
    if record["exception"] is not None:
        payload["exception"] = str(record["exception"])
    print(json.dumps(payload, default=str), file=sys.stdout)


def configure_logging(level: str = "INFO") -> None:
    logger.remove()
    logger.configure(patcher=_inject_request_id)
    logger.add(_json_sink, level=level)

