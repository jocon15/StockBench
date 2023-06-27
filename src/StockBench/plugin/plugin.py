import os
import logging
import importlib
from typing import Callable, Any
from abc import abstractmethod

log = logging.getLogger()


class PluginInterface:

    @abstractmethod
    def get_strategy_name(self):
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_data_name(self):
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_trigger(self):
        raise NotImplementedError('Not implemented yet!')

    @abstractmethod
    def get_subplot(self):
        raise NotImplementedError('Not implemented yet!')


# right now the function does not return anything so None
# ... indicates that the args for each callable are unknown
# REMEMBER: this is just typing information for the dict
# this has to be a global variable and not defined inside a class
# because external plugins will not have access to the pacakge manager instance
# (there may be a way to pass the instance into the plugin, but we don't want to do that)
plugin_initialization_funcs: dict[str, Callable[..., PluginInterface]] = {}


# FIXME: register and unregister is deprecated (here and in __init__.py files)
class PluginManager:
    # FIXME: register and unregister is deprecated (here and in __init__.py files)
    @staticmethod
    def register(name: str, creation_func: Callable[..., PluginInterface]):
        plugin_initialization_funcs[name] = creation_func

    # FIXME: register and unregister is deprecated (here and in __init__.py files)
    @staticmethod
    def unregister(name: str):
        # None is for: do nothing if there is nothing to pop - don't throw error
        plugin_initialization_funcs.pop(name, None)

    @staticmethod
    def import_module(filepath: str):
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
            plugin = PluginManager.import_module(plugin_path)
            # call initialize fxn to register each plugin with the plugin dict
            init_dict = plugin.initialize()
            for key in init_dict.keys():
                # call the constructor for the class reference given (turns classes into objects)
                init_dict[key] = init_dict[key]()

            # add the init dict to the plugin dict
            initialized_plugins = {**initialized_plugins, **init_dict}
        return initialized_plugins
