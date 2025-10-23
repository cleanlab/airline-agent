"""Helpers to manage warnings emitted by llama-index."""

import warnings
from collections.abc import Iterator
from contextlib import contextmanager

from pydantic.warnings import UnsupportedFieldAttributeWarning


@contextmanager
def suppress_llama_index_warnings() -> Iterator[None]:
    """
    A context manager to silence warnings that llama-index causes during import time.

    This is a workaround until https://github.com/run-llama/llama_index/pull/20122 fixes the root cause.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UnsupportedFieldAttributeWarning,
            module=r"pydantic\._internal\._generate_schema",
        )
        yield
