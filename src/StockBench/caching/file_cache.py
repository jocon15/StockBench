import os
import json

CACHE_FILE_FILEPATH = 'cache.json'


def load_cache_file():
    if not os.path.exists(CACHE_FILE_FILEPATH):
        empty_dict = {}
        with open(CACHE_FILE_FILEPATH, 'w+') as file:
            json.dump(empty_dict, file, indent=4)
