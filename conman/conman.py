import argparse
import json
import os
from ConfigParser import SafeConfigParser
import yaml


class ConMan(object):
    def __init__(self, config_files=(), environment_override=False):
        """Initialize with config files

        :param iterable config_files: a list of config file names
        :param bool environment_override: can environment variable override
                                          named values from the config files?

        You may choose not to initialize with any config files and add
        them later using add_config_file(), which is more sophisticated.

        ConMan works with multiple file formats and will try all of them
        until one succeeds or all of them fail.
        """
        self._conf = None
        self._environment_override = environment_override
        for config_file in config_files:
            self.add_config_file(config_file)

    def add_config_file(self,
                        filename,
                        env_variable=None,
                        command_line_argument=None,
                        file_type=None):
        """Add a configuration file

        :param str filename: absolute or relative path
        :param str base_dir: join with filename if not None
        :param str env_variable: if not None contains filename
        :param str command_line_argument: if not None contains filename
        :param str file_type: valid values are- 'yaml', 'json', 'ini'

        There are many ways to tell ConMan about a configuration and there is
        a search path with options to override. Here are the rules:

        The filename contains the path to the config file. It may be
        overridden by an environment variable if provided, which can be
        overridden by a command line argument. If a file type is provided
        it is used to determine how to parse the config file. If no file type
        is provided ConMan will try to guess by the extension.
        """
        if env_variable:
            filename = os.getenv(env_variable, filename)

        if command_line_argument:
            parser = argparse.ArgumentParser()
            parser.add_argument(command_line_argument, dest='filename')
            args = parser.parse_known_args()
            filename = args.filename

        if not file_type:
            file_type = self._guess_file_type(filename)

        process_func = getattr(self, '_process_%s_file' % file_type)
        process_func(filename)

    def _guess_file_type(self, filename):
        """Guess the file type based on its extension

        :param str filename: the config filename
        :returns: the file type of the config file

        The extension is extracted and matched against known extensions.
        If the extension matches no known file type an exception is raised.

        """
        ext = os.path.splitext(filename)[1][1:]
        return dict(yml='yaml',
                    yaml='yaml',
                    json='json',
                    ini='ini')[ext]

    def _process_ini_file(self, filename):
        parser = SafeConfigParser()
        parser.read(filename)
        for section_name in parser.sections():
            self._conf[section_name] = {}
            section = self._conf[section_name]
            for name, value in parser.items(section_name):
                section[name] = value

    def _process_json_file(self, filename):
        self._conf = json.loads(filename)

    def _process_yaml_file(self, filename):
        self._conf = yaml.loads(filename)






