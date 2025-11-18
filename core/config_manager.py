#!/usr/bin/env python3
"""
Configuration Manager for Professional Patch Tool
Handles all configuration loading, saving, and validation
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages tool configuration with validation and defaults"""
    
    DEFAULT_CONFIG = {
        "auto_backup": True,
        "confirm_applications": True,
        "max_preview_lines": 50,
        "enable_syntax_hints": True,
        "backup_keep_days": 30,
        "show_hidden_files": False,
        "enable_advanced_features": False,
        "backup_rotation_count": 10
    }
    
    CONFIG_VALIDATION = {
        "auto_backup": {"type": bool},
        "confirm_applications": {"type": bool},
        "max_preview_lines": {"type": int, "min": 10, "max": 200},
        "enable_syntax_hints": {"type": bool},
        "backup_keep_days": {"type": int, "min": 1, "max": 365},
        "show_hidden_files": {"type": bool},
        "enable_advanced_features": {"type": bool},
        "backup_rotation_count": {"type": int, "min": 1, "max": 100}
    }

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.config_file = os.path.join(base_path, '.patch_config.json')
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file with validation"""
        config = self.DEFAULT_CONFIG.copy()

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Validate and merge user configuration
                for key, value in user_config.items():
                    if key in self.CONFIG_VALIDATION:
                        if self._validate_config_value(key, value):
                            config[key] = value
                        else:
                            print(f"⚠️  Invalid config value for '{key}': {value}, using default")
                
            except Exception as e:
                print(f"⚠️  Config load error: {e}, using defaults")

        return config

    def _validate_config_value(self, key: str, value: Any) -> bool:
        """Validate a configuration value against schema"""
        validation = self.CONFIG_VALIDATION.get(key, {})
        
        if "type" in validation and not isinstance(value, validation["type"]):
            return False
        
        if validation.get("type") == int:
            if "min" in validation and value < validation["min"]:
                return False
            if "max" in validation and value > validation["max"]:
                return False
        
        return True

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value with validation"""
        if key not in self.CONFIG_VALIDATION:
            print(f"❌ Unknown configuration key: {key}")
            return False
        
        if not self._validate_config_value(key, value):
            print(f"❌ Invalid value for configuration '{key}': {value}")
            return False
        
        self.config[key] = value
        return True

    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save_config()
