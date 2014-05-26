import json
import os
import yaml
import tempfile
from unittest import TestCase
from conman.conman import ConMan


def _make_config_file(file_type, content):
    # create temp filename
    f = tempfile.NamedTemporaryFile(suffix=file_type, delete=False)
    # write content
    f.write(content)

    # return filename
    return f.name


def _make_ini_file(valid, extension=None):
    valid_text = '[ini_conf]\nkey = value\n'
    invalid_text = 'vdgdfhf bt'

    content = valid_text if valid else invalid_text
    file_type = extension if extension else '.ini'
    return _make_config_file(file_type, content)



def _make_json_file(valid, extension=None):
    valid_text = json.dumps(dict(json_conf=dict(key='value')))
    invalid_text = 'vdgdfhf bt'

    content = valid_text if valid else invalid_text
    file_type = extension if extension else '.json'
    return _make_config_file(file_type, content)



def _make_yaml_file(valid, extension=None):
    valid_text = yaml.dump(dict(yaml_conf=dict(key='value')))
    invalid_text = 'vdgdfhf bt'

    content = valid_text if valid else invalid_text

    file_type = extension if extension else '.yaml'
    return _make_config_file(file_type, content)


class ConmanTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._good_files = {}
        cls._good_files['ini'] = _make_ini_file(True)
        cls._good_files['json'] = _make_json_file(True)
        cls._good_files['yaml'] = _make_yaml_file(True, extension='txt')

        cls._bad_files = {}
        cls._bad_files['ini'] = _make_ini_file(False)
        cls._bad_files['json'] = _make_json_file(False)
        cls._bad_files['yaml'] = _make_yaml_file(False)

    @classmethod
    def tearDownClass(cls):
        for f in cls._good_files.values() + cls._bad_files.values():
            os.remove(f)

    def setUp(self):
        self.conman = ConMan()

    def tearDown(self):
        pass

    def test_guess_file_type(self):
        f = self.conman._guess_file_type
        self.assertEqual('json', f('x.json'))
        self.assertEqual('yaml', f('x.yml'))
        self.assertEqual('yaml', f('x.yaml'))
        self.assertEqual('ini', f('x.ini'))
        self.assertIsNone(f('x.no_such_ext'))

    def test_init_no_files(self):
        self.assertItemsEqual({}, self.conman._conf)

    def test_init_some_good_files(self):
        c = ConMan(self._good_files.values())
        expected = dict(json_conf=dict(key='value'),
                        yaml_conf=dict(key='value'),
                        ini_conf=dict(key='value'))
        self.assertDictEqual(expected, c._conf)

    def test_init_some_bad_files(self):
        some_bad_files = self._good_files.values() + self._bad_files.values()
        self.assertRaises(Exception, ConMan, some_bad_files)

    def test_add_config_file_simple_with_file_type(self):
        c = self.conman
        c.add_config_file(self._good_files['ini'], file_type='ini')
        expected = dict(ini_conf=dict(key='value'))
        self.assertDictEqual(expected, c._conf)

    def test_add_config_file_simple_guess_file_type(self):
        c = self.conman
        c.add_config_file(self._good_files['ini'])
        expected = dict(ini_conf=dict(key='value'))
        self.assertDictEqual(expected, c._conf)

    def test_add_config_file_simple_wrong_file_type(self):
        c = self.conman
        c.add_config_file(self._good_files['ini'], file_type='json')
        expected = dict(ini_conf=dict(key='value'))
        self.assertDictEqual(expected, c._conf)

    def test_add_config_file_simple_unknown_wrong_file_type(self):
        c = self.conman
        c.add_config_file(self._good_files['ini'], file_type='asdf')
        expected = dict(ini_conf=dict(key='value'))
        self.assertDictEqual(expected, c._conf)

    def test_add_config_file_environment_override(self):
        os.environ['yaml_conf.key'] = 'env_value'
        c = ConMan(environment_override=True)
        c.add_config_file(self._good_files['yaml'])
        expected = dict(yaml_conf=dict(key='env_value'))
        self.assertDictEqual(expected, c._conf)

    def test_add_config_file_command_line_override(self):
        pass

    def test_add_config_file_command_line_bad_file_type(self):
        pass

    def test_add_config_file_command_line_bad_extension(self):
        pass

    def test_add_config_file_command_line_bad_environment_override(self):
        pass

    def test_add_config_file_command_line_bad_commandline_override(self):
        pass

    def test_environment_variable_override(self):
        pass

    def test_command_line_override(self):
        pass
