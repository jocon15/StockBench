import os
import logging
import importlib
from typing import Any

log = logging.getLogger()


class PluginManager:

    @staticmethod
    def import_module(filepath: str):
        # importlib uses .'s for delimiter
        # this is a path independent way of converting the os filepath to the importlib filepath
        if '\\' in filepath:
            filepath = filepath.replace('\\', '.')
        if '/' in filepath:
            filepath = filepath.replace('/', '.')
        return importlib.import_module(filepath)

    @staticmethod
    def load_plugins(plugin_dir: str) -> dict[str: Any]:
        # build the plugin paths
        plugin_paths = []
        try:
            if not os.path.isdir(plugin_dir):
                raise Exception('Path passed is not a folder!')
            for folder in os.listdir(plugin_dir):
                folder_path = os.path.join(plugin_dir, folder)
                if os.path.isdir(folder_path):
                    for file in os.listdir(folder_path):
                        filepath = os.path.join(folder_path, file)
                        if os.path.isfile(filepath) and file == '__init__.py':
                            plugin_paths.append(folder_path)
        except EnvironmentError as err:
            log.warning("Unable to read folder {folder}: {err}".format(folder=plugin_dir, err=err))

        # initialize and instantiate all the plugins
        initialized_plugins = {}
        for plugin_path in plugin_paths:
            # import the plugin
            plugin = PluginManager.import_module(plugin_path)

            # call initialize fxn to register each plugin with the plugin dict
            init_dict = plugin.initialize()

            # add the init dict to the plugin dict
            initialized_plugins = {**initialized_plugins, **init_dict}
        return initialized_plugins
