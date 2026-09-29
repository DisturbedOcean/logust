"""Objects with a callable ``write()`` are used as stream sinks."""

from __future__ import annotations

import contextlib
import io
import sys

import pytest

from logust import Logger, LogLevel
from logust._logust import PyLogger


class FlushCountingStream:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.flushes = 0

    def write(self, message: str) -> None:
        self.lines.append(message)

    def flush(self) -> None:
        self.flushes += 1


@pytest.fixture
def logger() -> Logger:
    logger = Logger(PyLogger(LogLevel.Trace))
    logger.disable()
    return logger


def test_stringio_sink(logger: Logger) -> None:
    stream = io.StringIO()
    logger.add(stream, format="{level} - {message}")

    logger.info("<green>hello</green>")
    logger.warning("world")

    assert stream.getvalue() == "INFO - hello\nWARNING - world\n"


def test_duck_typed_sink_is_flushed(logger: Logger) -> None:
    stream = FlushCountingStream()
    logger.add(stream, format="{message}")

    logger.info("one")
    logger.info("two")

    assert stream.lines == ["one\n", "two\n"]
    assert stream.flushes == 2


def test_redirected_stdout_object_receives_output(logger: Logger) -> None:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        logger.add(sys.stdout, format="{message}")
        logger.info("captured")

    assert buf.getvalue() == "captured\n"


def test_stream_sink_with_level_and_filter(logger: Logger) -> None:
    stream = io.StringIO()
    logger.add(
        stream,
        level="WARNING",
        format="{message}",
        filter=lambda record: "skip" not in record["message"],
    )

    logger.info("low")
    logger.warning("skip me")
    logger.error("kept")

    assert stream.getvalue() == "kept\n"


def test_stream_sink_remove(logger: Logger) -> None:
    stream = io.StringIO()
    handler_id = logger.add(stream, format="{message}")

    logger.info("before")
    assert logger.remove(handler_id) is True
    logger.info("after")

    assert stream.getvalue() == "before\n"


def test_stream_sink_includes_traceback(logger: Logger) -> None:
    stream = io.StringIO()
    logger.add(stream, format="{message}")

    try:
        raise ValueError("bad")
    except ValueError:
        logger.exception("boom")

    output = stream.getvalue()
    assert output.startswith("boom\n")
    assert "ValueError: bad" in output
    assert output.endswith("\n")


def test_callable_sink_includes_traceback(logger: Logger) -> None:
    messages: list[str] = []
    logger.add(messages.append, format="{message}")

    try:
        raise ValueError("bad")
    except ValueError:
        logger.exception("boom")

    assert len(messages) == 1
    assert messages[0].startswith("boom\n")
    assert "ValueError: bad" in messages[0]
