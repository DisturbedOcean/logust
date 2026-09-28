"""Color markup is stripped from non-colorized output."""

from __future__ import annotations

from pathlib import Path

import pytest

from logust import Logger, LogLevel
from logust._logust import PyLogger


@pytest.fixture
def logger() -> Logger:
    logger = Logger(PyLogger(LogLevel.Trace))
    logger.disable()
    return logger


def test_callable_sink_strips_markup(logger: Logger) -> None:
    messages: list[str] = []
    logger.add(messages.append, format="{message}")

    logger.info("<green>hello</green> <bold>world</bold> <nope>x</nope>")

    assert messages == ["hello world <nope>x</nope>"]


def test_callable_sink_with_filter_strips_markup(logger: Logger) -> None:
    messages: list[str] = []
    logger.add(messages.append, format="{message}", filter=lambda _: True)

    logger.info("<red>hello</red>")

    assert messages == ["hello"]


def test_file_sink_strips_markup(logger: Logger, tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    logger.add(str(log_file), format="{message}")

    logger.info("<green>hello</green>")
    logger.complete()

    assert log_file.read_text() == "hello\n"
