# Roborock Plus

Provides human-friendly HA services for Roborock vacuums that the official
integration doesn't expose (yet).

Built as a thin **proxy** over `vacuum.send_command` — it piggybacks on the
official integration's already-established V1 WebSocket/AES connection, so
no duplicate cloud login, no duplicate device discovery.

## Requirements

Official HA core **Roborock** integration must already be installed and
connected. This integration simply waits for it (`after_dependencies: roborock`)
and registers extra services.

## Services

| Service | Params | What it does |
|---|---|---|
| `roborock_plus.resolve_error` | `entity_id`, `error_code` (optional) | Clear a latched error (tap "Resolved" in the Roborock app). Accepts numeric code or enum name like `dirty_tank_latch_open`, `filter_screen_exception`. Omit `error_code` to let the device auto-clear its current error. |
| `roborock_plus.change_volume` | `entity_id`, `volume` (0-100) | Change robot voice volume. |
| `roborock_plus.dnd_close` | `entity_id` | Turn off Do-Not-Disturb schedule right now. |
| `roborock_plus.reset_consumable` | `entity_id`, `which` (list, optional) | Reset consumable counters (`main_brush`, `side_brush`, `filter`, `sensor`). |
| `roborock_plus.get_status` | `entity_id` | Pull raw V1 device status JSON. |
| `roborock_plus.get_consumable` | `entity_id` | Pull consumable remaining-time JSON. |

## Auto-clear error automation (drop-in for your existing script)

Replace `auto_clear_dirty_tank_error` action with `roborock_plus.resolve_error`
— accepts enum names directly, no Jinja2 mapping needed:

```yaml
- service: roborock_plus.resolve_error
  target:
    entity_id: vacuum.yi_lou_sao_di_ji
  data:
    error_code: "{{ states('sensor.yi_lou_sao_di_ji_vacuum_error') != 'none' and states('sensor.yi_lou_sao_di_ji_vacuum_error') or states('sensor.yi_lou_sao_di_ji_dock_dock_error') }}"
```

## Deployment

```bash
# Copy to HA custom_components
scp -r custom_components/roborock_plus user@ha:/config/custom_components/

# Or use HACS: Add repository → Custom repositories → ha-roborock-plus
```

## License

MIT
