"""
asyncio
"""
from __future__ import annotations

import asyncio
import enum
import logging
import datetime
from typing import (
    Any,
    Generic,
    cast,
    Callable,
    Awaitable,
    NamedTuple,
    Final,
    TypeVar
)
from .const import (
    EVENT_CORE_START
)

_LOGGER = logging.getLogger(__name__)

_T = TypeVar("_T")
_R = TypeVar("_R")
_R_co = TypeVar("_R_co", covariant = True)

class CoreJobType(enum.Enum):
    """ Job Type """
    CoroutineFunction = 1
    Callback = 2
    Executor = 3


class CoreJob(Generic[_R_co]):
    """Job to be run later"""

    def __init__(self, target: Callable[..., _R_co]) -> None:
        """ Initialize Job Object """
        self.target = target
        self.job_type = _get_callable_job_type(target)


def _get_callable_job_type(target: Callable[..., Any]) -> CoreJobType:
    """Determine the Job Type from the Callable"""
    check_target = target
    
    if asyncio.iscoroutinefunction(check_target):
        return CoreJobType.CoroutineFunction
    return CoreJobType.Executor


class CoreState(enum.Enum):
    """Core의 현재 상태"""

    not_running = "NOT_RUNNING"
    starting = "STARTING"
    running = "RUNNING"
    stopping = "STOPPING"
    stopped = "STOPPED"

    def __str__(self) -> str:
        return self.value


class Core:
    """Root Object"""

    def __init__(self) -> None:
        """새로운 Core Object를 init"""
        self.loop = asyncio.get_event_loop()
        self.bus = EventBus(self)
        self.states = StateMachine(self.bus, self.loop)
        self.state: CoreState = CoreState.not_running
        self.exit_code: int = 0

    def start(self) -> int:
        """Core 시작"""
        return self.exit_code

    async def async_run(self) -> int:
        """Main Entry Point"""
        if self.state != CoreState.not_running:
            raise RuntimeError("Core is already running")

        await self.async_start()

        return self.exit_code

    async def async_start(self) -> None:
        """ 이벤트 루프 안에서 시작 과정 종료 """
        _LOGGER.info("Starting Program Core")

        self.state = CoreState.starting
        self.bus.async_fire(EVENT_CORE_START)

    def async_add_core_job(
        self, corejob: CoreJob[Awaitable[_R] | _R], *args: Any
    ) -> asyncio.Future[_R] | None:
        """Add a CoreJob from within the Event Loop"""
        task: asyncio.Future[_R]
        if corejob.job_type == CoreJobType.CoroutineFunction:
            task = self.loop.create_task(
                cast(Callable[..., Awaitable[_R]], corejob.target)(*args)
            )
        elif corejob.job_type == CoreJobType.Callback:
            self.loop.call_soon(corejob.target, *args)
            return None
        else:
            task = self.loop.run_in_executor(
                None, cast(Callable[..., _R], corejob.target), *args
            )
        
        return task


class Event:
    """Event"""

    def __init__(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        time_fired: datetime.datetime | None =  None
    ) -> None:
        """Initialize new Event"""
        self.event_type = event_type
        self.data = data or {}
        self.time_fired = time_fired or datetime.datetime.now()


class _FilterableJob(NamedTuple):
    """Event Listener Job to be executed with Optional Filter"""

    job: CoreJob[None | Awaitable[None]]
    event_filter: Callable[[Event], bool] | None

class EventBus:
    """ Allow the firing of and listening for events """

    def __init__(self, core: Core) -> None:
        """ Initialize new Event Bus """
        self._listeners: dict[str, list[_FilterableJob]] = {}
        self._core = core

    def async_fire(
        self,
        event_type: str,
        event_data: dict[str, Any] | None = None,
        time_fired: datetime.datetime | None = None
    ) -> None:
        """ Fire an Event
        """
        listeners = self._listeners.get(event_type, [])
        print(listeners)

        event = Event(
            event_type = event_type,
            data = event_data,
            time_fired = time_fired
        )

        if not listeners:
            print("listeners empty")
            return

        for job, event_filter in listeners:
            self._core.async_add_core_job(job, event)


class StateMachine:
    """ State Machine """

    def __init__(self, bus: EventBus, loop: asyncio.events.AbstractEventLoop) -> None:
        """ Initialize State machine """
        self._bus = bus
        self._loop = loop

    def async_set(
        self,
        entity_id: str,
        new_state: str
    ) -> None:
        """Set state of and entity"""


class Behavior:
    """Callable Behavior"""

    def __init__(self) -> None:
        pass


class BehaviorRepeater:
    """ Behavior Repeater """

    def __init__(self, core: Core) ->  None:
        """ Initialize Behavior Repeater """
        self._core = core
