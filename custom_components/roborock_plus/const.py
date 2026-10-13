"""Constants and error code lookups for Roborock Plus."""

from __future__ import annotations

DOMAIN = "roborock_plus"

# V1 vacuum_error enum → numeric codes (python-roborock RoborockErrorCode)
# Used so services can accept either a string name or a numeric code.
VACUUM_ERROR_CODES: dict[str, int] = {
    "none": 0,
    "lidar_blocked": 1,
    "bumper_stuck": 2,
    "wheels_suspended": 3,
    "cliff_sensor_error": 4,
    "main_brush_jammed": 5,
    "side_brush_jammed": 6,
    "wheels_jammed": 7,
    "robot_trapped": 8,
    "no_dustbin": 9,
    "strainer_error": 10,
    "compass_error": 11,
    "low_battery": 12,
    "charging_error": 13,
    "battery_error": 14,
    "wall_sensor_dirty": 15,
    "robot_tilted": 16,
    "side_brush_error": 17,
    "fan_error": 18,
    "dock": 19,
    "optical_flow_sensor_dirt": 20,
    "vertical_bumper_pressed": 21,
    "dock_locator_error": 22,
    "return_to_dock_fail": 23,
    "nogo_zone_detected": 24,
    "visual_sensor": 25,
    "light_touch": 26,
    "vibrarise_jammed": 27,
    "robot_on_carpet": 28,
    "filter_blocked": 29,
    "invisible_wall_detected": 30,
    "cannot_cross_carpet": 31,
    "internal_error": 32,
    "collect_dust_error_3": 34,
    "collect_dust_error_4": 35,
    "mopping_roller_1": 36,
    "mopping_roller_error_2": 37,
    "clear_water_box_hoare": 38,
    "dirty_water_box_hoare": 39,
    "sink_strainer_hoare": 40,
    "clear_water_box_exception": 41,
    "clear_brush_exception": 42,
    "clear_brush_exception_2": 43,
    "filter_screen_exception": 44,
    "mopping_roller_2": 45,
    "up_water_exception": 48,
    "drain_water_exception": 49,
    "temperature_protection": 51,
    "clean_carousel_exception": 52,
    "clean_carousel_water_full": 53,
    "water_carriage_drop": 54,
    "check_clean_carouse": 55,
    "audio_error": 56,
}

# V1 dock_error enum → numeric codes (python-roborock RoborockDockErrorCode)
DOCK_ERROR_CODES: dict[str, int] = {
    "ok": 0,
    "no_dustbin_or_filter": 32,
    "auto_empty_dock_fan_error": 33,
    "duct_blockage": 34,
    "auto_empty_dock_voltage_error": 35,
    "water_empty": 38,
    "waste_water_tank_full": 39,
    "maintenance_brush_jammed": 42,
    "dirty_tank_latch_open": 44,
    "no_dustbin": 46,
    "cleaning_tank_full_or_blocked": 53,
}


def resolve_code(name_or_code: str | int, mapping: dict[str, int]) -> int:
    """Accept either a numeric code (int) or a string enum name; return numeric code."""
    if isinstance(name_or_code, int):
        return name_or_code
    try:
        return int(name_or_code)
    except (ValueError, TypeError):
        return mapping.get(str(name_or_code), -1)
