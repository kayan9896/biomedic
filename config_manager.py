import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = {}
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self, config_path: str = './config.json'):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self._config = json.load(f)
                print(f"Configuration loaded from {config_path}")
            else:
                print(f"Config file not found at {config_path}. Using defaults.")
                self._config = {
                    "on_simultation": True,
                    "mode": 0,
                    "imu_on": True,
                    "imu_port": "COM3",
                    "glyph_on": True,
                    "framegrabber_device": "OBS Virtual Camera",
                    "framegrabber_autocollect": True,
                    "calibphantom_design": "abc'",
                    "model_simdata_path": "./",
                    "template_path": "./",
                    "carm_folder": "./carm",
                    "backend_pixel": 1024,
                    "ui_pixel": 960
                }
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Set defaults if loading fails

    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
    