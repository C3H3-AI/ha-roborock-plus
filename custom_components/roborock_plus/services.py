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

VACUUM_ENTITY = vol.All(cv.ensure_list, [cv.entity_id])

# ---------- resolve_error ----------
def _resolve_error_schema(call: ServiceCall) -> dict[str, Any]:
    """Build params dict, accepting either vacuum or dock error codes."""
    raw_code = call.data.get("error_code")
    if raw_code is None:
        return {}
    # Accept int, or string enum name from either mapping
    v = resolve_code(raw_code, VACUUM_ERROR_CODES)
    if v == -1:
        v = resolve_code(raw_code, DOCK_ERROR_CODES)
    if v == -1:
        raise HomeAssistantError(
            f"Unknown error_code {raw_code!r}. Use a numeric code or a known enum name "
            f"(vacuum: filter_screen_exception, dock: dirty_tank_latch_open, etc.)."
        )
    return {"error_code": v}

async def async_resolve_error(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Resolve a latched error (tap 'Resolved' in Roborock app)."""
    entity = call.data["entity_id"]
    params = _resolve_error_schema(call)
    _LOGGER.info("roborock_plus.resolve_error → %s, params=%s", entity, params)
    return await hass.services.async_call(
        "vacuum", "send_command",
        {"entity_id": entity, "command": "resolve_error", "params": params or {}},
        blocking=True, return_response=True,
    )

# ---------- change_volume ----------
async def async_change_volume(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    volume = int(call.data["volume"])
    entity = call.data["entity_id"]
    _LOGGER.info("roborock_plus.change_volume → %s volume=%s", entity, volume)
    return await hass.services.async_call(
        "vacuum", "send_command",
        {"entity_id": entity, "command": "change_sound_volume", "params": {"volume": volume}},
        blocking=True, return_response=True,
    )

# ---------- close_dnd_timer ----------
async def async_dnd_close(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    entity = call.data["entity_id"]
    _LOGGER.info("roborock_plus.dnd_close → %s", entity)
    return await hass.services.async_call(
        "vacuum", "send_command",
        {"entity_id": entity, "command": "close_dnd_timer", "params": {}},
        blocking=True, return_response=True,
    )

# ---------- reset_consumable ----------
async def async_reset_consumable(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    entity = call.data["entity_id"]
    which = call.data.get("which", ["main_brush", "side_brush", "filter", "sensor"])
    _LOGGER.info("roborock_plus.reset_consumable → %s %s", entity, which)
    return await hass.services.async_call(
        "vacuum", "send_command",
        {"entity_id": entity, "command": "reset_consumable", "params": which},
        blocking=True, return_response=True,
    )

# ---------- get_status ----------
async def async_get_status(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    entity = call.data["entity_id"]
    _LOGGER.info("roborock_plus.get_status → %s", entity)
    return await hass.services.async_call(
        "vacuum", "send_command",
        {"entity_id": entity, "command": "get_status", "params": {}},
        blocking=True, return_response=True,
    )

# ---------- get_consumable ----------
async def async_get_consumable(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    entity = call.data["entity_id"]
    _LOGGER.info("roborock_plus.get_consumable → %s", entity)
    return await hass.services.async_call(
        "vacuum", "send_command",
        {"entity_id": entity, "command": "get_consumable", "params": {}},
        blocking=True, return_response=True,
    )


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register Roborock Plus services."""

    hass.services.async_register(
        DOMAIN, "resolve_error", async_resolve_error,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("error_code"): vol.Any(int, str),
        }),
        supports_response=True,
    )

    hass.services.async_register(
        DOMAIN, "change_volume", async_change_volume,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("volume"): vol.All(int, vol.Range(min=0, max=100)),
        }),
        supports_response=True,
    )

    hass.services.async_register(
        DOMAIN, "dnd_close", async_dnd_close,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
        supports_response=True,
    )

    hass.services.async_register(
        DOMAIN, "reset_consumable", async_reset_consumable,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("which", default=["main_brush", "side_brush", "filter", "sensor"]):
                [vol.In(["main_brush", "side_brush", "filter", "sensor"])],
        }),
        supports_response=True,
    )

    hass.services.async_register(
        DOMAIN, "get_status", async_get_status,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
        supports_response=True,
    )

    hass.services.async_register(
        DOMAIN, "get_consumable", async_get_consumable,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
        supports_response=True,
    )

    _LOGGER.info("Roborock Plus services registered: resolve_error, change_volume, "
                 "dnd_close, reset_consumable, get_status, get_consumable")
