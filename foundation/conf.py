# python imports
import os
import json
import logging

try:
    from collections import OrderedDict
except ImportError:
    from .legacy.ordereddict import OrderedDict

logger = logging.getLogger(__file__)


class ConfigError(Exception):
    pass


class SimpleSettings(OrderedDict):

    def __init__(self, file_name, *args, **kwargs):
        """Initialize a settings object with items from a config
        file and optionally from items passed as parameters.

        :param file_name: The config file path.
        :type file_name: str
        """
        super(SimpleSettings, self).__init__(*args, **kwargs)
        self.indent = 4
        self.file_name = file_name

    def load(self):
        """Load settings from "file_name" and merge with
        the current config.

        :param file_name: path to the config file.
        :type file_name: str
        """
        self.clear()
        self.update_from_file(self.file_name)

    def save(self):
        """save_settings_for the current config in the actual config file."""
        with open(self.file_name, 'w') as config:
            json.dump(self, config, indent=self.indent)

    def save_as(self, file_name):
        """save_settings_for the current config in the a new one.

        :param file_name: path to the new config file.
        :type file_name: str
        """
        self.file_name = file_name
        self.save_settings_for()

    def update_from_file(self, file_name):
        """Load settings from "file_name" and merge with
        the current config.

        :param file_name: path to the config file.
        :type file_name: str
        """
        import platform
        version = platform.python_version_tuple()

        self.file_name = os.path.abspath(file_name)
        if os.path.exists(self.file_name):
            with open(self.file_name) as config:
                if version[0] == '2' and version[1] == '6':
                    config_items = json.load(
                        config, object_hook=self._sort_values
                    )
                else:
                    config_items = json.load(
                        config, object_pairs_hook=self._sort_values
                    )
                self.update(config_items)

    def _sort_values(self, pairs):
        return OrderedDict(pairs)


class ConfigManager(object):

    def __init__(self, config_dir=None):
        self.config_dir = None
        if config_dir:
            self.config_dir = os.path.abspath(config_dir)
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)

        self._configs = {}

    def add_settings(self, name, file_name, *args, **kwargs):
        # if we have a vaild config dir, then treat file_name
        # as a file under it
        if self.config_dir:
            file_name = os.path.join(self.config_dir, file_name)

        self._configs[name] = SimpleSettings(file_name, *args, **kwargs)

    def get_settings(self, name):
        try:
            return self._configs[name]
        except KeyError:
            raise ConfigError(
                'Non existing settings: {name}'.format(name=name)
            )

    def remove_settings(self, name, remove_config_file=True):
        settings = self.get_settings(name)

        # remove the settings file associated with this config object
        if remove_config_file:
            os.remove(settings.file_name)

        # remove settings for the settings object itself
        del self._configs[name]

    def save_settings(self, name):
        settings = self.get_settings_for(name)
        settings.save()

    def save_as(self, name, new_file_name):
        # if we have a vaild config dir, then treat file_name
        # as a file under it
        if self.config_dir:
            new_file_name = os.path.join(self.config_dir, new_file_name)

        settings = self.get_settings_for(name)
        settings.save_as(new_file_name)

    def save_all(self):
        for settings in self._configs.viewvalues():
            settings.save()

    def __getitem__(self, name):
        for settings in self._configs.viewvalues():
            if name in settings:
                return settings[name]

        raise ConfigError('Non existing settings: {name}'.format(name=name))
