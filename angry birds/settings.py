import json
import os

DEFAULT_CONFIG = {
  "window": {
    "width": 1080,
    "height": 720,
    "caption": "blud birds",
    "fps": 60
  },
  "game": {
    "attempts": 3,
    "level_count": 3
  },
  "anchor": [175, 450],
  "physics": {
    "gravity": [0, 700],
    "damping": 0.82,
    "collision_slop": 0.05,
    "collision_bias": 0.4,
    "settle_velocity": 10.0,
    "settle_angular_velocity": 0.5,
    "settle_time": 1.0
  },
  "bird": {
    "mass": 0.5,
    "radius": 15,
    "elasticity": 0.7,
    "friction": 0.5,
    "launch_multiplier": 8.0,
    "max_pull": 125,
    "grab_radius": 30,
    "offscreen_margin": 100,
    "trajectory_frames": 250,
    "trajectory_step": 2,
    "trajectory_dot_radius": 3
  },
  "pig": {
    "mass": 0.5,
    "attached_mass": 0.2,
    "radius": 20,
    "elasticity": 0.5,
    "friction": 0.5,
    "death_impulse": 70,
    "laugh_frame_ms": 250,
    "laugh_min_ms": 2000,
    "laugh_max_ms": 5000,
    "laugh_volume": 0.2
  },
  "blocks": {
    "size": 60,
    "mass": 0.18,
    "elasticity": 0.5,
    "friction": 0.5,
    "spawn_padding": 16,
    "shell_thickness": 1.75,
    "break_velocity": 200
  },
  "explosion": {
    "radius": 500,
    "duration_ms": 300,
    "strength": 25,
    "start_radius": 12,
    "grow_radius": 58,
    "max_alpha": 220,
    "ring_width": 4
  },
  "spawn": {
    "cell_x_min": 11,
    "cell_x_max": 15,
    "y_common_min": 8,
    "y_common_max": 10,
    "y_mid_min": 6,
    "y_mid_max": 7,
    "y_top": 5,
    "common_chance": 0.7,
    "mid_chance": 0.9,
    "max_attempts": 500
  },
  "levels": {
    "1": [[12, 10, "wood"], [13, 10, "wood"], [12.5, 9, "pig_wood"]],
    "2": [
      [12, 10, "wood"], [13, 10, "pig_wood"], [12, 9, "wood"],
      [13, 9, "wood"], [12.5, 8, "pig_wood"]
    ],
    "3": [
      [11, 10, "wood"], [12, 10, "wood"], [13, 10, "pig_wood"],
      [14, 10, "wood"], [15, 10, "wood"], [11.5, 9, "pig_wood"],
      [12.5, 9, "wood"], [13.5, 9, "wood"], [14.5, 9, "wood"],
      [12, 8, "wood"], [13, 8, "pig_wood"], [14, 8, "wood"],
      [12.5, 7, "wood"], [13.5, 7, "wood"], [13, 6, "pig_wood"]
    ]
  }
}

def _merge(base, override):
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and key in merged:
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged

def _validate(value, default):
    if isinstance(default, dict):
        source = value if isinstance(value, dict) else {}
        return {
            key: _validate(source.get(key, default[key]), default[key])
            for key, item in default.items()
        }
    if isinstance(default, bool):
        return value if isinstance(value, bool) else default
    if isinstance(default, int):
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        return default
    if isinstance(default, float):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return default
    if isinstance(default, list):
        return value if isinstance(value, list) else default
    if isinstance(default, str):
        return value if isinstance(value, str) else default
    return value if type(value) is type(default) else default

def load_config(path=None):
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "..", "config.json")

    try:
        with open(path, encoding="utf-8") as handle:
            loaded = json.load(handle)
    except (FileNotFoundError, PermsisionError, OSerror) as error:
        print(f"[config] using built-in defaults ({error})")
        return _validate({}, DEFAULT_CONFIG)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        print("[config] config.json must contain an object, using defaults")
        return _validate({}, DEFAULT_CONFIG)

    return _validate(_merge(DEFAULT_CONFIG, loaded), DEFAULT_CONFIG)

CONFIG = load_config()




WIDTH = 1080
HEIGHT = 720

COLOR = (0, 0, 0)
GROUND_COLOR = (51, 0, 0)
BIRD_COLOR = (51, 51, 255, 255)
PIG_COLOR = (254, 204, 153, 255)
WOOD_COLOR = (150, 90, 40, 255)
GRID_COLOR = (100, 100, 100, 255)


BLOCK_SIZE = 60
GRID_SIZE = BLOCK_SIZE
BLOCK_MASS = 0.18
BLOCK_ELASTICITY = 0.5
BLOCK_FRICTION = 0.5
SPAWN_PADDING = 16
MIN_CENTER_DISTANCE = BLOCK_SIZE + SPAWN_PADDING

PIG_CATEGORY = 2
PIG_WOOD_CATEGORY = 4
PIG_COLLISION_TYPE = 10
PIG_DEATH_IMPULSE = 70
PIG_LAUGH_FRAME_MS = 250

EXPLOSION_RADIUS = 500
EXPLOSION_DURATION = 300

ANCHOR_POS = (175, 450)
PIG_POS = (800, 570)
