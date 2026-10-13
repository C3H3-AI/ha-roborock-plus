"""Roborock Plus — thin proxy services that wrap vacuum.send_command.

Each service here directly forwards to the Roborock integration's V1 RPC
channel through HA's built-in `vacuum.send_command` platform service.
This avoids duplicate cloud login and piggybacks on the official
integration's already-established WebSocket/AES connection.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, callback
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, VACUUM_ERROR_CODES, DOCK_ERROR_CODES, resolve_code

_LOGGER = logging.getLogger(__name__)


def _resolve_error_code(raw_code: Any) -> int:
    """Accept int / str number / str enum name, return numeric error code."""
    v = resolve_code(raw_code, VACUUM_ERROR_CODES)
    if v == -1:
        v = resolve_code(raw_code, DOCK_ERROR_CODES)
    if v == -1:
        raise HomeAssistantError(
            f"Unknown error_code {raw_code!r}. Use a numeric code or a known enum name "
            f"(vacuum: filter_screen_exception, dock: dirty_tank_latch_open, etc.)."
        )
    return v


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register Roborock Plus services (闭包捕获 hass)."""

    async def _fire(entity: str, command: str, params: Any) -> None:
        """Forward the command to vacuum.send_command.

        Must use async_call — the blocking hass.services.call() from inside
        the event loop deadlocks (it synchronously waits on a coroutine that
        itself needs the loop).
        """
        await hass.services.async_call(
            "vacuum", "send_command",
            {"entity_id": entity, "command": command, "params": params},
            blocking=True, return_response=False,
        )

    # ---------- resolve_error ----------
    async def _resolve_error(call: ServiceCall) -> ServiceResponse:
        entity = call.data["entity_id"]
        raw = call.data.get("error_code")
        params = {"error_code": _resolve_error_code(raw)} if raw is not None else {}
        _LOGGER.info("roborock_plus.resolve_error → %s, params=%s", entity, params)
        await _fire(entity, "resolve_error", params)
        return {"status": "ok", "entity": entity, "command": "resolve_error",
                "params": params}

    # ---------- change_volume ----------
    async def _change_volume(call: ServiceCall) -> ServiceResponse:
        volume = int(call.data["volume"])
        entity = call.data["entity_id"]
        _LOGGER.info("roborock_plus.change_volume → %s volume=%s", entity, volume)
        await _fire(entity, "change_sound_volume", {"volume": volume})
        return {"status": "ok", "entity": entity, "command": "change_sound_volume",
                "params": {"volume": volume}}

    # ---------- close_dnd_timer ----------
    async def _dnd_close(call: ServiceCall) -> ServiceResponse:
        entity = call.data["entity_id"]
        _LOGGER.info("roborock_plus.dnd_close → %s", entity)
        await _fire(entity, "close_dnd_timer", {})
        return {"status": "ok", "entity": entity, "command": "close_dnd_timer"}

    # ---------- reset_consumable ----------
    async def _reset_consumable(call: ServiceCall) -> ServiceResponse:
        entity = call.data["entity_id"]
        which = call.data.get("which", ["main_brush", "side_brush", "filter", "sensor"])
        _LOGGER.info("roborock_plus.reset_consumable → %s %s", entity, which)
        await _fire(entity, "reset_consumable", which)
        return {"status": "ok", "entity": entity, "command": "reset_consumable",
                "params": which}

    # ---------- get_status ----------
    async def _get_status(call: ServiceCall) -> ServiceResponse:
        entity = call.data["entity_id"]
        _LOGGER.info("roborock_plus.get_status → %s", entity)
        await _fire(entity, "get_status", {})
        return {"status": "ok", "entity": entity, "command": "get_status"}

    # ---------- get_consumable ----------
    async def _get_consumable(call: ServiceCall) -> ServiceResponse:
        entity = call.data["entity_id"]
        _LOGGER.info("roborock_plus.get_consumable → %s", entity)
        await _fire(entity, "get_consumable", {})
        return {"status": "ok", "entity": entity, "command": "get_consumable"}

    # ---------- 注册 ----------
    # supports_response=False（默认）— REST API 层不会预检查 return_response 兼容性
    hass.services.async_register(
        DOMAIN, "resolve_error", _resolve_error,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("error_code"): vol.Any(int, str),
        }),
    )

    hass.services.async_register(
        DOMAIN, "change_volume", _change_volume,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("volume"): vol.All(int, vol.Range(min=0, max=100)),
        }),
    )

    hass.services.async_register(
        DOMAIN, "dnd_close", _dnd_close,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
    )

    hass.services.async_register(
        DOMAIN, "reset_consumable", _reset_consumable,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("which", default=["main_brush", "side_brush", "filter", "sensor"]):
                [vol.In(["main_brush", "side_brush", "filter", "sensor"])],
        }),
    )

    hass.services.async_register(
        DOMAIN, "get_status", _get_status,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
    )

    hass.services.async_register(
        DOMAIN, "get_consumable", _get_consumable,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
    )

    _LOGGER.info("Roborock Plus services registered: resolve_error, change_volume, "
                 "dnd_close, reset_consumable, get_status, get_consumable")
