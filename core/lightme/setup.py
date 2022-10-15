"""Methods for boot which is used for LightMe startup."""
from __future__ import annotations
import asyncio
import contextlib
from datetime import timedelta

import logging
from typing import Any, Awaitable, Callable, Generator
from timeit import default_timer as timer
from termcolor import colored

from lightme.util import ensure_unique_string
from . import core, loader, config as config_util
from .typing import ConfigType
from .util import dt as dt_util
from .const import (
    EVENT_COMPONENT_LOADED,
    ATTR_COMPONENT,
    EVENT_LIGHTME_START
)

COMPONENT = "component"

DATA_SETUP_STARTED = "setup_started"
DATA_SETUP_DONE = "setup_done"
DATA_SETUP_TIME = "setup_time"
DATA_SETUP = "setup_tasks"

SLOW_SETUP_MAX_LIMIT = 300

_LOGGER = logging.getLogger(__name__)

async def async_setup_component(
    lightme: core.LightMe, domain: str, config: ConfigType
) -> bool:
    """Setup components."""

    print(colored(f"Start of {domain}...", 'yellow'))
    # return True if component is already in Config object
    if domain in lightme.config.components:
        print(colored(f"Return true for {domain}"), 'yellow')
        return True

    setup_tasks: dict[str, asyncio.Task[bool]] = lightme.data.setdefault(DATA_SETUP, {})
    print(colored(f"Setup Tasks: {setup_tasks}", 'white'))

    # If domain is already registered in tasks, set up them.
    if domain in setup_tasks:
        print(f"Domain {domain} in setup_tasks")
        return await setup_tasks[domain]

    task = setup_tasks[domain] = lightme.async_create_task(
        _async_setup_component(lightme, domain, config)
    )
    print(colored(f"[Task] {task}", 'white'))
    print(colored(f"...End of {domain}", 'yellow'))

    try:
        result = await task
        print(
            colored(
                f"'{result}' with task {task.get_coro()} - [setup.py: async_setup_component]",
                'yellow'
            )
        )
        return result
    finally:
        if domain in lightme.data.get(DATA_SETUP_DONE, {}):
            lightme.data[DATA_SETUP_DONE].pop(domain).set()
        print(
            colored(
            f"Finished setting up components {domain} - [setup.py: async_setup_component]",
            'blue'
            )
        )

async def _async_setup_component(
    lightme: core.LightMe, domain: str, config: ConfigType
) -> bool:
    """Setup component from domain."""

    application: loader.Application | None = None

    try:
        application = await loader.async_get_application(lightme, domain)
        print(
            colored(
            f"Start setting up component '{application.domain}'"
            + " - [setup.py: _async_setup_component]",
            'blue'
            )
        )
    except loader.ApplicationNotFound:
        _LOGGER.error(colored(f"Application '{application}' failed to load.", 'red'))
        return False

    #TODO: Need to handle dependencies or requirements here later.
    # try:
    #     await async_process_deps_reqs(hass, config, integration)
    # except HomeAssistantError as err:
    #     log_error(str(err))
    #     return False

    # Check application has no problem while import.
    try:
        component = application.get_component()
    except ImportError as error:
        _LOGGER.error(
            "Failed to import component: %s", error
        )
        return False

    processed_config = await config_util.async_process_component_config(
        lightme, config, application
    )

    # Start of Setup.
    start = timer()
    _LOGGER.info("Setting up %s", domain)
    with async_start_setup(lightme, domain):
        task = None
        result: Any | bool = True
        try:
            if hasattr(component, "async_setup"):
                task = component.async_setup(lightme, processed_config)
            elif hasattr(component, "setup"):
                task = lightme.loop.run_in_executor(
                    None, component.setup, lightme, processed_config
                )
            elif not hasattr(component, "async_user_default"):
                _LOGGER.error(colored("No setup or user default function defined.", 'red'))
                return False

            if task:
                async with lightme.timeout.async_timeout(SLOW_SETUP_MAX_LIMIT, domain):
                    result = await task
        except asyncio.TimeoutError:
            _LOGGER.error(
                "Setting up %s is taking over than %s seconds.", domain, 300
            )
            return False
        finally:
            end = timer()
        _LOGGER.info("Setup of domain %s took %.1f seconds", domain, end - start)

        if result is False:
            _LOGGER.error(
                "Application failed to initialize."
            )
            return False
        if result is not True:
            _LOGGER.error(
                "Application %s did not return boolean if setup was "
                "successful. Disabling component.", domain
            )
            return False

    # Clean up.
    if domain in lightme.data[DATA_SETUP]:
        lightme.data[DATA_SETUP].pop(domain)

    lightme.bus.async_fire(EVENT_COMPONENT_LOADED, {COMPONENT: domain})

    return True

@core.callback
def async_when_setup(
    lightme: core.LightMe,
    component: str,
    when_setup_cb: Callable[[core.LightMe, str], Awaitable[None]]
) -> None:
    """Call a method when a component is setup."""

    _async_when_setup(lightme, component, when_setup_cb, False)

@core.callback
def async_when_setup_or_start(
    lightme: core.LightMe,
    component: str,
    when_setup_cb: Callable[[core.LightMe, str], Awaitable[None]]
) -> None:
    """Call a method when a component is setup or state is fired."""

    _async_when_setup(lightme, component, when_setup_cb, True)

@core.callback
def _async_when_setup(
    lightme: core.LightMe,
    component: str,
    when_setup_cb: Callable[[core.LightMe, str], Awaitable[None]],
    start_event: bool
) -> None:
    """Call a method when component is setup or start event fires."""

    async def when_setup() -> None:
        """Call the callback."""
        try:
            await when_setup_cb(lightme, component)
        except Exception:
            _LOGGER.exception("Error handling when_setup callback for %s", component)

    if component in lightme.config.components:
        lightme.async_create_task(when_setup())
        return

    listeners: list[core.CALLBACK_TYPE] = []

    async def _matched_event(event: core.Event) -> None:
        """Call the callback when matched an event."""

        for listener in listeners:
            listener()
        await when_setup()

    async def _loaded_event(event: core.Event) -> None:
        """Call the callback if loaded the expected component."""

        if event.data[ATTR_COMPONENT] == component:
            await _matched_event(event)

    listeners.append(lightme.bus.async_listen(EVENT_COMPONENT_LOADED, _loaded_event))
    if start_event:
        listeners.append(
            lightme.bus.async_listen(EVENT_LIGHTME_START, _matched_event)
        )

@contextlib.contextmanager
def async_start_setup(
    lightme: core.LightMe, domain: str
) -> Generator[None, None, None]:
    """Keep track of when setup starts and finishes."""

    setup_started = (
        # dictionary to store which component started setup and its started time.
        lightme.data.setdefault(DATA_SETUP_STARTED, {})
    )
    started = dt_util.utcnow()

    # If there's no same domain in setup_started, set unique_domain as domain.
    # else, append number at the end of domain and set as unique_domain.
    unique_domain = ensure_unique_string(domain, setup_started)
    setup_started[unique_domain] = started

    yield

    setup_time: dict[str, timedelta] = lightme.data.setdefault(DATA_SETUP_TIME, {})
    time_taken = dt_util.utcnow() - started
    # Delete data with key unique_domain form setup_started.
    del setup_started[unique_domain]
    if "." in domain:
        _, driver = domain.split(".", 1)
    else:
        driver = domain
    if driver in setup_time:
        setup_time[driver] += time_taken
    else:
        setup_time[driver] = time_taken
