"""This class manages multiple configuration files in several file formats

It provides a read-only access and just exposes a nested dict
Supported file formats: Ini,  Json and Yaml
"""
import os
import json
import yaml
from configparser import ConfigParser
from conman.conman_base import ConManBase

FILE_TYPES = 'ini json yaml'.split()


class ConManFile(ConManBase):
    def __init__(self, config_files=()):
        """Initialize with config files

        :param iterable config_files: a list of config file names or
            environment variables that contain file names.

        You may choose not to initialize with any config files and add
        them later using add_config_file(), which is more sophisticated.

        ConMan works with multiple file formats and will try all of them
        until one succeeds or all of them fail.
        """
        ConManBase.__init__(self)
        self._config_files = []
        for config_file in config_files:
            self.add_config_file(config_file)

    def add_config_file(self,
                        filename=None,
                        env_variable=None,
                        base_dir=None,
                        file_type=None):
        """Add a configuration file

        :param str filename: absolute or relative path to a config file
        :param str env_variable: env var that contains a config filename
        :param str base_dir: join with filename if not None
        :param str env_variable: if not None contains filename
        :param str file_type: valid values are- 'yaml', 'json', 'ini'

        There are many ways to tell ConMan about a configuration.
        Here are the rules:

        The filename contains the path to the config file. The filename may
        also be read from an environment variable. Either filename is not None
        or environment_Variable are not None, but not both.

        If base_dir is not None then it will combined with the config filename
        to create an absolute path.

        If a file type is provided it is used to determine how to parse the
        config file. If no file type is provided ConMan will try to guess by
        the extension.
        """
        if filename is None and env_variable is None:
            raise Exception('filename and env_variable are both None')

        if filename is not None and env_variable is not None:
            raise Exception('filename and env_variable are both not None')

        if filename in self._config_files:
            raise Exception('filename is already in the config file list')

        if env_variable:
            filename = os.environ[env_variable]

        if base_dir:
            filename = os.path.join(base_dir, filename)

        if not os.path.isfile(filename):
            raise Exception('No such file: ' + filename)

        if not file_type:
            file_type = self._guess_file_type(filename)

        file_types = set(FILE_TYPES)
        if file_type:
            try:
                return self._process_file(filename, file_type)
            except Exception:
                # Remove failed file_type from set of file types to try
                if file_type in file_types:
                    file_types.remove(file_type)

        # If no file type can be guessed or guess failed try all parsers
        for file_type in file_types:
            try:
                return self._process_file(filename, file_type)
            except Exception:
                pass

        raise Exception('Bad config file: ' + filename)

    def _guess_file_type(self, filename):
        """Guess the file type based on its extension

        :param str filename: the config filename
        :returns: the file type of the config file or None

        The extension is extracted and matched against known extensions.
        If the extension matches no known file type return None
        """
        ext = os.path.splitext(filename)[1][1:]
        return dict(yml='yaml',
                    yaml='yaml',
                    json='json',
                    ini='ini').get(ext, None)

    def _process_file(self, filename, file_type):
        process_func = getattr(self, '_process_%s_file' % file_type)
        process_func(filename)

    def _process_ini_file(self, filename):
        parser = ConfigParser()
        parser.read(filename)
        for section_name in parser.sections():
            self._conf[section_name] = {}
            section = self._conf[section_name]
            for name, value in parser.items(section_name):
                section[name] = value

    def _process_json_file(self, filename):
        with open(filename) as f:
            self._conf.update(json.load(f))

    def _process_yaml_file(self, filename):
        with open(filename) as f:
            self._conf.update(yaml.full_load(f))
