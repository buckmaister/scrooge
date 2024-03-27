import json
import sys


def load_config():
    try:
        with open('config/config.json', 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print("File config.json not found, check file and path.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error decoding JSON from config.json.")
        sys.exit(1)


def update_value(key_path, new_value):
    """
    Updates a value in the JSON configuration file.

    :param key_path: The path to the key in the dictionary, separated by periods (e.g. "SPREADSHEET.SHEET_ID").
    :param new_value: The new value to set.
    :return:
    """
    config = load_config()

    keys = key_path.split('.')
    d = config
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = new_value

    try:
        with open('config/config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)
        print(f"Value for '{key_path}' updated successfully.")
    except Exception as e:
        print(f"Failed to update config file: {e}")


CONFIG = load_config()




