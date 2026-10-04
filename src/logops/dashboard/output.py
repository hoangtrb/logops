"""Where the pages draw: Streamlit by default, or an HTML builder while a report is rendered.

Pages import `st` from here. Each thread (and task) has its own target, so a report built on a
worker thread never touches the dashboard a viewer is using at the same time.
"""

import contextvars
from contextlib import contextmanager

import streamlit

_TARGET = contextvars.ContextVar("output", default=streamlit)


class _Output:
    def __getattr__(self, name: str):
        return getattr(_TARGET.get(), name)


st = _Output()


@contextmanager
def drawing_to(target):
    """Send every `st.*` call made by the pages in this thread to `target`."""
    token = _TARGET.set(target)
    try:
        yield target
    finally:
        _TARGET.reset(token)
