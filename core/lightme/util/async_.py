"""Asyncio utilities"""
from __future__ import annotations

from asyncio.events import AbstractEventLoop
import concurrent.futures
import threading
import logging
from typing import Any, Callable, TypeVar

_LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")

def run_callback_threadsafe(
    loop: AbstractEventLoop, callback: Callable[..., _T], *args: Any
) -> concurrent.futures.Future[_T]:
    """Submit a callback object to a given event loop."""

    ident = loop.__dict__.get("_thread_ident")
    if ident is not None and ident == threading.get_ident():
        raise RuntimeError("Cannot be called from inside the event loop.")

    future: concurrent.futures.Future[_T] = concurrent.futures.Future()

    def run_callback() -> None:
        """Run callback and store result."""
        try:
            future.set_result(callback(*args))
        except Exception as error: # pylint: disable=broad-except
            if future.set_running_or_notify_cancel():
                future.set_exception(error)
            else:
                _LOGGER.warning(
                    "Exception on lost future: ", exc_info=True
                )

    loop.call_soon_threadsafe(run_callback)

    return future
