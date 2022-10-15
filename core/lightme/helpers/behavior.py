"""Behavior-Call helpers."""
from __future__ import annotations

from typing import Awaitable, Callable
import voluptuous as vol

from lightme.core import BehaviorCall, LightMe, callback

@callback
def async_register_admin_behavior(
    lightme: LightMe,
    domain: str,
    behavior: str,
    behavior_func: Callable[[BehaviorCall], Awaitable[None] | None],
    schema: vol.Schema = vol.Schema({}, extra=vol.PREVENT_EXTRA)
) -> None:
    """Register a behavior which requires admin permission."""

    async def admin_handler(call: BehaviorCall) -> None:
        """"""
        if call.context.user_id:
            user = await lightme.auth.async_get_user(call.context.user_id)

    lightme.behaviors.async_register(domain, behavior, admin_handler, schema=schema)
