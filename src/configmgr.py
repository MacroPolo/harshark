import json
import os.path

class ConfigMgr(object):
 
    def __init__(self):
        self.config = None
        self._factory_default = {
          "case-sensitive-matching": False,
          "cell-colorization": True,
          "colour_scheme": {
            "bookmark": "#ffffff",
            "default": "#ffffff",
            "method": {
              "connect": "#8dd3c7",
              "delete": "#fb8072",
              "get": "#ffffff",
              "head": "#ccebc5",
              "options": "#ffed6f",
              "patch": "#d9d9d9",
              "post": "#80b1d3",
              "put": "#fdb462",
              "trace": "#fccde5"
            },
            "protocol": {
              "http": "#fdb462",
              "https": "#ffffff",
              "wss": "#ccebc5",
              "ws": "#fdb462",
              "ftp": "#80b1d3"
            },
            "search_match": "#ffff99",
            "status": {
              "100": "#8dd3c7",
              "200": "#ffffff",
              "300": "#80b1d3",
              "400": "#fdb462",
              "500": "#fb8072"
            }
          },
          "experimental-saml": False,
          "sort-headers": False,
          "truncate-character-count": 5000,
          "word-wrap": True,
          "table_columns": {
            "connection-id": {
              "category": "General",
              "index": 3,
              "name": "Connection ID",
              "visible": False
            },
            "http-version-request": {
              "category": "Request",
              "index": 7,
              "name": "HTTP Version (Request)",
              "visible": False
            },
            "http-version-response": {
              "category": "Response",
              "index": 11,
              "name": "HTTP Version (Response)",
              "visible": True
            },
            "mime-type": {
              "category": "Response",
              "index": 10,
              "name": "MIME-Type",
              "visible": True
            },
            "protocol": {
              "category": "Request",
              "index": 5,
              "name": "Protocol",
              "visible": True
            },
            "redirect-url": {
              "category": "Response",
              "index": 12,
              "name": "Redirect URL",
              "visible": False
            },
            "request-body-size": {
              "category": "Request",
              "index": 14,
              "name": "Request Body Size",
              "visible": True
            },
            "request-header-size": {
              "category": "Request",
              "index": 13,
              "name": "Request Header Size",
              "visible": True
            },
            "request-id": {
              "category": "General",
              "index": 0,
              "name": "Request ID",
              "visible": False
            },
            "request-method": {
              "category": "Request",
              "index": 4,
              "name": "Request Method",
              "visible": True
            },
            "response-body-size": {
              "category": "Response",
              "index": 16,
              "name": "Response Body Size",
              "visible": True
            },
            "response-body-size-uncompressed": {
              "category": "Response",
              "index": 17,
              "name": "Response Body Size (Uncompressed)",
              "visible": False
            },
            "response-header-szie": {
              "category": "Response",
              "index": 15,
              "name": "Response Header Size",
              "visible": True
            },
            "server-ip": {
              "category": "General",
              "index": 2,
              "name": "Server IP",
              "visible": True
            },
            "status-code": {
              "category": "Response",
              "index": 8,
              "name": "Status Code",
              "visible": True
            },
            "status-text": {
              "category": "Response",
              "index": 9,
              "name": "Status Text",
              "visible": False
            },
            "time-blocked": {
              "category": "Timing",
              "index": 19,
              "name": "Time Blocked",
              "visible": False
            },
            "time-connect": {
              "category": "Timing",
              "index": 21,
              "name": "Time Connect",
              "visible": False
            },
            "time-dns": {
              "category": "Timing",
              "index": 20,
              "name": "Time DNS",
              "visible": False
            },
            "time-receive": {
              "category": "Timing",
              "index": 24,
              "name": "Time Receive",
              "visible": False
            },
            "time-send": {
              "category": "Timing",
              "index": 22,
              "name": "Time Send",
              "visible": False
            },
            "time-ssl": {
              "category": "Timing",
              "index": 25,
              "name": "Time SSL",
              "visible": False
            },
            "time-total": {
              "category": "Timing",
              "index": 18,
              "name": "Time Total",
              "visible": True
            },
            "time-wait": {
              "category": "Timing",
              "index": 23,
              "name": "Time Wait",
              "visible": False
            },
            "timestamp": {
              "category": "General",
              "index": 1,
              "name": "Timestamp",
              "visible": True
            },
            "url": {
              "category": "Request",
              "index": 6,
              "name": "URL",
              "visible": True
            }
          }
        }

        base_path = os.path.join(os.path.dirname(__file__), '..')
        self._config_path = os.path.join(base_path, 'config', 'config.json')

        if not os.path.isfile(self._config_path):
            self._createDefault()

        self._loadConfig()

    def _createDefault(self):
        with open(self._config_path, 'w') as f:
            json.dump(self._factory_default, f, indent=4, sort_keys=True)

    def _loadConfig(self):
        with open(self._config_path, 'r') as f:
            self.config = json.load(f)

    def getConfig(self, key):
        return self.config.get(key)

    def setConfig(self, key, value):
        self.config[key] = value
        self._saveConfig()

    def _saveConfig(self):
        with open(self._config_path, 'w') as f:
            json.dump(self.config, f, indent=4, sort_keys=True)

