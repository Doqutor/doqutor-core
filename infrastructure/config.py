import json
from getpass import getuser
import secrets
from copy import deepcopy

DEFAULT_CONFIG = {
        'prefix': getuser() + '-' + secrets.token_hex(3)
}

def get_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except IOError:
        print("Config doesn't exist yet, generating new config...")
        with open("config.json", "w") as f:
            json.dump(DEFAULT_CONFIG, f)
        return deepcopy(DEFAULT_CONFIG)
    except:
        raise Exception("Something else is wrong with your config. Try deleting and recreating it.")
    
