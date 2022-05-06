import json
import lib.settings as settings

def importConfig(file):
    with open(file, 'r') as f:
        settings.config = json.load(f)
    return 1