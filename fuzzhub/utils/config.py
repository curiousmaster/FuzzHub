"""
File: fuzzhub/utils/config.py

Configuration loader for FuzzHub.
"""

import os
import yaml

_CONFIG_CACHE = None


def _load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    config_path = os.path.join(project_root, "config", "config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_config():
    global _CONFIG_CACHE

    if _CONFIG_CACHE is None:
        _CONFIG_CACHE = _load_config()

    return _CONFIG_CACHE
