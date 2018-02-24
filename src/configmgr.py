import json
import os.path
import sys

class ConfigMgr(object):
 
    def __init__(self):
        self.config = None
        base_path = os.path.join(os.path.dirname(__file__), '..')
        self._config_path = os.path.join(base_path, 'config', 'config.json')
        self._loadConfig()

    def _loadConfig(self):
        try:
            with open(self._config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print('No configuration file found in config directory!')
            sys.exit(1)

    def getConfig(self, key):
        return self.config.get(key)

    def setConfig(self, key, value):
        self.config[key] = value
        self._saveConfig()

    def _saveConfig(self):
        with open(self._config_path, 'w') as f:
            json.dump(self.config, f, indent=4, sort_keys=True)

