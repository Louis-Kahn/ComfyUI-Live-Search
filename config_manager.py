import os
import json

class ConfigManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'api_config.json')
    
    def get_config(self):
        try:
            if not os.path.exists(self.config_path):
                return {}
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[LiveSearch] Error loading config: {e}")
            return {}

    def save_config(self, config):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[LiveSearch] Error saving config: {e}")
            return False

    def get_api_key(self, provider_name, node_input_key=None):
        """
        Helper to get API key from input (priority) or config file
        """
        # 1. Check if provided directly in node input
        if node_input_key and isinstance(node_input_key, str) and node_input_key.strip():
            return node_input_key.strip()
        
        # 2. Check config file
        config = self.get_config()
        key_name = f"{provider_name.lower()}_api_key"
        return config.get(key_name, "")

