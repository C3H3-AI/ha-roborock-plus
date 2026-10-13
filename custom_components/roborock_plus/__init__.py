"""Roborock Plus integration — thin wrapper around HA core roborock V1 RPC."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Roborock Plus services from YAML (not used, supports config_entries only)."""
    _LOGGER.info("Roborock Plus async_setup called")
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Roborock Plus from a config entry."""
    _LOGGER.info("Roborock Plus async_setup_entry called (entry=%s)", entry.title)
    async_setup_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
