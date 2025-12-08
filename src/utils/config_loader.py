"""
Configuration loader utilities
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Load YAML configuration file.
    
    Args:
        config_path: Path to YAML config file
    
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_model_config(config_dir: str = "config") -> Dict[str, Any]:
    """
    Load model configuration.
    
    Args:
        config_dir: Directory containing config files
    
    Returns:
        Model configuration dictionary
    """
    config_path = Path(config_dir) / "model_config.yaml"
    return load_yaml_config(str(config_path))


def get_language_rules(config_dir: str = "config") -> Dict[str, Any]:
    """
    Load language rules configuration.
    
    Args:
        config_dir: Directory containing config files
    
    Returns:
        Language rules dictionary
    """
    config_path = Path(config_dir) / "language_rules.yaml"
    return load_yaml_config(str(config_path))
