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
    
    def _load_config(self, config_path: str = './config/config.json'):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self._config = json.load(f)
                from confirmap_dataclasses.confirmap_data import SystemConfigClass 
                s = SystemConfigClass(**self._config)
                print(f"Configuration loaded from {config_path}", s)
            else:
                print(f"Config file not found at {config_path}. Using defaults.")
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Set defaults if loading fails

    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
    