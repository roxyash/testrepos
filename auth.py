import json


def read_config(config_file='settings.json'):
    """Метод чтения, settings.json, для получения кредов. """
    with open(config_file, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data


creds = read_config()
url = creds['instance_url']
