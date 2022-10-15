"""
Core Functions for LightMe
"""
from __future__ import annotations

import asyncio
import enum
import functools
import logging
import datetime
import re
import os
from time import monotonic
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    NamedTuple,
    TypeVar,
    cast
)
from termcolor import colored

import voluptuous as vol

from .exceptions import (
    LightMeError
)

from .const import (
    EVENT_LIGHTME_STARTED,
    EVENT_CORE_CONFIG_UPDATE,
    EVENT_LIGHTME_START,
    EVENT_LIGHTME_CLOSE,
    EVENT_LIGHTME_STOP,
    EVENT_BEHAVIOR_REGISTERED,
    ATTR_DOMAIN,
    ATTR_BEHAVIOR,
    UNIT_SYSTEM_IMPERIAL
)
from .util import dt as dt_util
from .util.async_ import (
    run_callback_threadsafe
)
from .util.timeout import TimeoutManager
from .util.unit_system import IMPERIAL_SYSTEM, METRIC_SYSTEM, UnitSystem

if TYPE_CHECKING:
    from .components.http import LightMeHTTP

if TYPE_CHECKING:
    from .user_defaults import UserDefaults

_T = TypeVar("_T")
_R = TypeVar("_R")
_R_co = TypeVar("_R_co", covariant = True)

_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])
CALLBACK_TYPE = Callable[[], None]

DOMAIN = 'lightme'

# How long to wait to log tasks that are blocking
BLOCK_LOG_TIMEOUT = 5
# How long to wait until things that run on startup have to finish.
TIMEOUT_EVENT_START = 2

class ConfigSource(enum.Enum):
    """Source of core configuration."""

    DEFAULT = "default"
    YAML = "yaml"

_LOGGER = logging.getLogger(__name__)

# Regex for Entity ID. (abc3.abcd03)
VALID_ENTITY_ID = re.compile(r"^(?!.+__)(?!_)[\da-z_]+(?<!_)\.(?!_)[\da-z_]+(?<!_)$")

def valid_entity_id(entity_id: str) -> bool:
    """Test if an entity ID is a valid format.

    Format: <domain>.<entity> where both are slugs.
    """
    return VALID_ENTITY_ID.match(entity_id) is not None

def callback(func: _CallableT) -> _CallableT:
    """Annotation to mark method as safe to call from inside the event loop."""

    setattr(func, "_lightme_callback", True)
    return func

def is_callback(func: Callable[..., Any]) -> bool:
    """Determine if function is safe to be called inside the event loop."""

    return getattr(func, "_lightme_callback", False) is True

@enum.unique
class LightMeJobType(enum.Enum):
    """Job Type"""

    CoroutineFunction = 1
    Callback = 2
    Executor = 3


class LightMeJob(Generic[_R_co]):
    """Job to be run later."""

    __slots__ = ("job_type", "call")

    def __init__(self, call: Callable[..., _R_co]) -> None:
        """Init a new Job object."""
        if asyncio.iscoroutine(call):
            raise ValueError("Coroutine is not allowed to be passed to LightMeJob")

        self.call = call
        self.job_type = _get_callable_job_type(call)

    def __repr__(self) -> str:
        """Return job."""
        return f"<Job {self.job_type} {self.call}"


def _get_callable_job_type(call: Callable[..., Any]) -> LightMeJobType:
    """Inspect job type from callable."""

    inspect_call = call
    while isinstance(inspect_call, functools.partial):
        inspect_call = inspect_call.func

    if asyncio.iscoroutinefunction(inspect_call):
        return LightMeJobType.CoroutineFunction
    if is_callback(inspect_call):
        return LightMeJobType.Callback
    return LightMeJobType.Executor

class CoreState(enum.Enum):
    """Core's current state"""

    not_running = "NOT_RUNNING"
    starting = "STARTING"
    running = "RUNNING"
    stopping = "STOPPING"
    stopped = "STOPPED"

    def __str__(self) -> str:
        return self.value


class LightMe:
    """Root object of LightMe."""

    http: LightMeHTTP = None
    user_defaults: UserDefaults = None

    def __init__(self) -> None:
        """Initialize a new Core object."""
        self.loop = asyncio.get_event_loop()
        self._pending_tasks: list[asyncio.Future[Any]] = []
        self._track_task = True
        self.bus = EventBus(self)
        self.behaviors = BehaviorRelay(self)
        self.states = StateMachine(self.bus, self.loop)
        self.data: dict[str, Any] = {}
        self.state: CoreState = CoreState.not_running
        self.config = Config(self)
        self.exit_code: int = 0
        self._stopped: asyncio.Event | None = None
        self.timeout = TimeoutManager()

    @property
    def is_running(self) -> bool:
        """Return true if LightMe is running."""

        return self.state in (CoreState.starting, CoreState.running)

    async def async_run(self) -> int:
        """LightMe main entry point."""

        if self.state != CoreState.not_running:
            raise RuntimeError("LightMe is already running")

        self._stopped = asyncio.Event()

        await self.async_start()

        await self._stopped.wait()
        return self.exit_code

    async def async_start(self) -> None:
        """Startup from inside the event loop."""

        _LOGGER.info("Starting LightMe")

        self.state = CoreState.starting
        self.bus.async_fire(EVENT_CORE_CONFIG_UPDATE)
        self.bus.async_fire(EVENT_LIGHTME_START)

        try:
            # Only block for EVENT_LIGHTME_START listener
            self.async_stop_track_tasks()
            async with self.timeout.async_timeout(TIMEOUT_EVENT_START):
                await self.async_block_till_done()
        except asyncio.TimeoutError:
            _LOGGER.warning(
                "Something is blocking LightMe from wrapping up."
            )

        print(self._pending_tasks)

        self.state = CoreState.running
        self.bus.async_fire(EVENT_CORE_CONFIG_UPDATE)
        self.bus.async_fire(EVENT_LIGHTME_STARTED)

    @callback
    def async_add_lightme_job(
        self, lightme_job: LightMeJob[Awaitable[_R] | _R], *args:  Any
    ) -> asyncio.Future[_R] | None:
        """Add LightMeJob from inside the event loop."""

        task: asyncio.Future[_R]
        if lightme_job.job_type == LightMeJobType.CoroutineFunction:
            task = self.loop.create_task(
                cast(Callable[..., Awaitable[_R]], lightme_job.call)(*args)
            )
        elif lightme_job.job_type == LightMeJobType.Callback:
            self.loop.call_soon(lightme_job.call, *args)
            return None
        else:
            task = self.loop.run_in_executor(
                None, cast(Callable[..., _R], lightme_job.call), *args
            )

        if self._track_task:
            self._pending_tasks.append(task)

        return task

    def async_create_task(self, call: Awaitable[_R]) -> asyncio.Task[_R]:
        """Create a task and add to pending list from inside the event loop."""

        task = self.loop.create_task(call)
        print(f"Task {task} from {call} created - [core.py: async_create_task]")

        if self._track_task:
            self._pending_tasks.append(task)

        return task

    def async_add_executor_job(
        self, call: Callable[..., _T], *args: Any
    ) -> asyncio.Future[_T]:
        """Add an executor job from inside the event loop."""

        task = self.loop.run_in_executor(None, call, *args)

        if self._track_task:
            self._pending_tasks.append(task)

        return task

    @callback
    def async_track_tasks(self) -> None:
        """Start tracking tasks."""
        self._track_task = True

    @callback
    def async_stop_track_tasks(self) -> None:
        """Stop tracking tasks."""
        self._track_task = False

    async def async_block_till_done(self) -> None:
        """Block until all pending work is done."""

        # To flush out any call_soon_threadsafe
        await asyncio.sleep(0)
        start_time: float | None = None

        while self._pending_tasks:
            pending = [task for task in self._pending_tasks if not task.done()]
            self._pending_tasks.clear()
            if pending:
                await self._await_and_log_pending(pending)

                if start_time is None:
                    # Avoid calling monotonic() until we know
                    # we may need to start logging blocked tasks.
                    start_time = 0
                elif start_time == 0:
                    # If we have waited twice then we set the start
                    # time
                    start_time = monotonic()
                elif monotonic() - start_time > BLOCK_LOG_TIMEOUT:
                    # We have waited at least three loops and new tasks
                    # continue to block. At this point we start
                    # logging all waiting tasks.
                    for task in pending:
                        _LOGGER.debug("Waiting for task: %s", task)
            else:
                await asyncio.sleep(0)

    async def _await_and_log_pending(self, pending: Iterable[Awaitable[Any]]) -> None:
        """Await and log tasks that take a long time."""

        wait_time = 0
        while pending:
            _, pending = await asyncio.wait(pending, timeout=BLOCK_LOG_TIMEOUT)
            if not pending:
                return
            wait_time += BLOCK_LOG_TIMEOUT
            for task in pending:
                _LOGGER.debug("Waited %s seconds for task: %s", wait_time, task)

    async def async_stop(self, exit_code: int = 0, *, force: bool = False) -> None:
        """Stop LightMe and shut down all threads."""

        if not force:
            if self.state == CoreState.not_running:
                return
            if self.state in [CoreState.stopping]:
                _LOGGER.info("LightMe is already stopping. Stopping request failed.")
            if self.state == CoreState.starting:
                _LOGGER.warning(
                    "LightMe is on startup process. Stopping request may fail."
                )

        self.state = CoreState.stopping
        self.bus.async_fire(EVENT_LIGHTME_STOP)

        self.exit_code = exit_code

        if self._stopped is not None:
            self._stopped.set()


class Event:
    """Event"""

    def __init__(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        time_fired: datetime.datetime | None =  None
    ) -> None:
        """Initialize a new Event object."""
        self.event_type = event_type
        self.data = data or {}
        self.time_fired = time_fired or datetime.datetime.now()


class _FilterableJob(NamedTuple):
    """Event listener job to be executed with optional filter."""

    job: LightMeJob[None | Awaitable[None]]
    event_filter: Callable[[Event], bool] | None


class Context:
    """The context that triggered semething."""

    __slots__ = ("user_id", "parent_id", "identifier", "origin_event")

    def __init__(
        self,
        user_id: str | None = None,
        parent_id: str | None = None,
        identifier: str | None = None
    ) -> None:
        """Init the context."""

        self.identifier = identifier
        self.user_id = user_id
        self.parent_id = parent_id
        self.origin_event: Event | None = None


class EventBus:
    """Allow the firing of and listening for events."""

    def __init__(self, lightme: LightMe) -> None:
        """Initialize a new Event Bus object."""
        self._listeners: dict[str, list[_FilterableJob]] = {}
        self._lightme = lightme

    @callback
    def async_listeners(self) -> dict[str, int]:
        """Retrieve dictionary with event and number of listeners."""
        return {key: len(listeners) for key, listeners in self._listeners.items()}

    @property
    def listeners(self) -> dict[str, int]:
        """Retrieve dictionary with event and number of listeners."""
        return run_callback_threadsafe(self._lightme.loop, self.async_listeners).result()

    @callback
    def async_fire(
        self,
        event_type: str,
        event_data: dict[str, Any] | None = None,
        time_fired: datetime.datetime | None = None
    ) -> None:
        """Fire an Event."""

        listeners = self._listeners.get(event_type, [])

        # EVENT_LIGHTME_CLOSE only to existing listeners (match_all_listeners)
        match_all_listeners = self._listeners.get("*")
        if match_all_listeners is not None and event_type != EVENT_LIGHTME_CLOSE:
            listeners = match_all_listeners + listeners

        event = Event(
            event_type=event_type,
            data=event_data,
            time_fired=time_fired
        )

        print(f"Firing Event: {event_type}")
        print(f"Listeners: {listeners}")
        print(f"Event: {event}")
        print("")

        _LOGGER.debug("Bus: Handling %s", event)

        if not listeners:
            return

        for job, event_filter in listeners:
            if event_filter is not None:
                try:
                    if not event_filter(event):
                        continue
                except Exception: # pylint: disable=broad-except
                    _LOGGER.exception("Error: event filter")
                    continue
            self._lightme.async_add_lightme_job(job, event)

    @callback
    def async_listen(
        self,
        event_type: str,
        listener: Callable[[Event], None | Awaitable[None]],
        event_filter: Callable[[Event], bool] | None = None,
        run_immediately: bool = False
    ) -> CALLBACK_TYPE:
        """Listen for all events or specific event."""

        if event_filter is not None and not is_callback(event_filter):
            raise LightMeError(f"Event filter {event_filter} is not a callback.")
        if run_immediately and not is_callback(listener):
            raise LightMeError(f"Event listener {listener} is not a callback.")
        return self._async_listen_filterable_job(
            event_type, _FilterableJob(LightMeJob(listener), event_filter, run_immediately)
        )

    @callback
    def _async_listen_filterable_job(
        self, event_type: str, filterable_job: _FilterableJob
    ) -> CALLBACK_TYPE:

        self._listeners.setdefault(event_type, []).append(filterable_job)

        def remove_listener() -> None:
            """Remove the listener."""

            self._async_remove_listener(event_type, filterable_job)

        return remove_listener

    @callback
    def async_listen_once(
        self, event_type: str, listener: Callable[[Event], None | Awaitable[None]]
    ) -> CALLBACK_TYPE:
        """Listen once for event of specific type."""

        async_remove_listener = run_callback_threadsafe(
            self._lightme.loop, self.async_listen_once, event_type, listener
        ).result()

        def remove_listener() -> None:
            """Remove listener."""
            run_callback_threadsafe(self._lightme.loop, async_remove_listener).result()

        return remove_listener

    @callback
    def _async_remove_listener(
        self, event_type: str, filterable_job: _FilterableJob
    ) -> None:
        """Remove a listener of a specific event_type."""

        try:
            self._listeners[event_type].remove(filterable_job)

            if not self._listeners[event_type]:
                self._listeners.pop(event_type)
        except (KeyError, ValueError):
            _LOGGER.exception(
                "Unable to remove unknown job listener %s", filterable_job
            )


class StateMachine:
    """ State Machine """

    def __init__(self, bus: EventBus, loop: asyncio.events.AbstractEventLoop) -> None:
        """Initialize a new State Machine object."""
        self._bus = bus
        self._loop = loop

    def async_set(
        self,
        entity_id: str,
        new_state: str
    ) -> None:
        """Set state of and entity."""


class Behavior:
    """Callable Behavior"""

    __slots__ = ["job", "schema"]

    def __init__(
        self,
        func: Callable[[BehaviorCall], Awaitable[None] | None],
        schema: vol.Schema | None
    ) -> None:
        """Init behavior."""
        self.job = LightMeJob(func)
        self.schema = schema

class BehaviorCall:
    """Representation of call to behavior."""

    __slots__ = ["domain", "behavior", "data", "context"]

    def __init__ (
        self,
        domain: str,
        behavior: str,
        data: dict[str, Any] | None = None,
        context: Context | None = None
    ) -> None:
        """Init behavior call."""
        self.domain = domain
        self.behavior = behavior
        self.data = data
        self.context = context or Context()

    def __repr__(self) -> str:
        """Return representation of behavior."""
        if self.data:
            return (
                f"<BehaviorCall {self.domain}.{self.behavior}"
            )

        return f"<Behaviorcall {self.domain}.{self.behavior}"

class BehaviorRelay:
    """Register behaviors to event bus."""

    def __init__(self, lightme: LightMe) ->  None:
        """Initialize a new Behavior Repeater object."""
        self._behaviors: dict[str, dict[str, Behavior]] = {}
        self._lightme = lightme

    @property
    def behaviors(self) -> dict[str, dict[str, Behavior]]:
        """Return dictionary with list of available behaviors."""

        return run_callback_threadsafe(self._lightme.loop, self.async_behaviors).result()

    @callback
    def async_behaviors(self) -> dict[str, dict[str, Behavior]]:
        """Return dictionary with list of available behaviors."""

        return {domain: behavior.copy() for domain, behavior in self._behaviors.items()}

    def register(
        self,
        domain: str,
        behavior: str,
        behavior_func: Callable[[BehaviorCall], Awaitable[None] | None]
    ) -> None:
        """Register a behavior."""

        run_callback_threadsafe(
            self._lightme.loop, self.async_register, domain, behavior, behavior_func
        ).result()

    @callback
    def async_register(
        self,
        domain: str,
        behavior: str,
        behavior_func: Callable[[BehaviorCall], Awaitable[None] | None],
        schema: vol.Schema | None = None
    ) -> None:
        """Register a behavior."""

        _behavior = Behavior(behavior_func, schema)

        print(f"Behavior Relay: {domain}.{behavior} - [core.py: async_register]")

        if domain in self._behaviors:
            self._behaviors[domain][behavior] = _behavior
        else:
            self._behaviors[domain] = {behavior: _behavior}

        self._lightme.bus.async_fire(
            EVENT_BEHAVIOR_REGISTERED, {ATTR_DOMAIN: domain, ATTR_BEHAVIOR: behavior}
        )

class Config:
    """Configuration settings"""

    def __init__(self, lightme: LightMe) -> None:
        """Initialize a new Config object."""
        self.lightme = lightme

        self.latitude: float = 0
        self.longitude: float = 0
        self.elevation: int = 0
        self.location_name: str = "Home"
        self.time_zone: str = "UTC"
        self.units: UnitSystem = METRIC_SYSTEM

        self.components: set[str] = set()
        self.config_dir: str | None = None

    def path(self, *path: str) -> str:
        """Retrieve configuration file's path."""

        if self.config_dir is None:
            raise LightMeError(
                "Configuration directory is not set in LightMe object"
            )
        return os.path.join(self.config_dir, *path)

    def set_time_zone(self, time_zone_str: str) -> None:
        """Set timezone."""
        if time_zone := dt_util.get_time_zone(time_zone_str):
            self.time_zone = time_zone_str
            dt_util.set_default_time_zone(time_zone)
        else:
            raise ValueError(f"Received invalid timezone {time_zone_str}")

    @callback
    def _update(
        self,
        *,
        latitude: float | None = None,
        longtitude: float | None = None,
        elevation: int | None = None,
        unit_system: str | None = None,
        location_name: str | None = None,
        time_zone: str | None = None
    ) -> None:
        """Update configuration from dictionary"""
        if latitude is not None:
            self.latitude = latitude
        if longtitude is not None:
            self.longitude = longtitude
        if elevation is not None:
            self.elevation = elevation
        if unit_system is not None:
            if unit_system == UNIT_SYSTEM_IMPERIAL:
                self.units = IMPERIAL_SYSTEM
            else:
                self.units = METRIC_SYSTEM
        if location_name is not None:
            self.location_name = location_name
        if time_zone is not None:
            self.set_time_zone(time_zone)

    async def async_load(self) -> None:
        """Load [lightme] core config."""

        print("WARNING: async_load config not implemented - core.py:async_load")
