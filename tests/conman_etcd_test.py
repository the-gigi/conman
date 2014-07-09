from unittest import TestCase
from conman.conman_etcd import ConManEtcd
from etcd_test_util import (start_local_etcd_server,
                            kill_local_etcd_server,
                            set_key,
                            delete_key)

class ConManEtcdTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Start local etcd server if not running
        start_local_etcd_server()

        # Add good key
        cls.good_dict = dict(a='1', b='Yeah, it works!!!')

    @classmethod
    def tearDownClass(cls):
        try:
            kill_local_etcd_server()
        except:  # noqa
            pass

    def setUp(self):
        self.conman = ConManEtcd()

        cli = self.conman.client
        delete_key(cli, 'good')
        delete_key(cli, 'refresh_test')
        set_key(cli, 'good', self.good_dict)

    def tearDown(self):
        delete_key(self.conman.client, 'good')
        delete_key(self.conman.client, 'refresh_test')

    def test_initialization(self):
        cli = self.conman.client
        self.assertEqual('http://127.0.0.1:4001', cli.base_uri)
        self.assertEqual(['http://127.0.0.1:4001'], cli.machines)
        self.assertEqual('127.0.0.1', cli.host)
        self.assertEqual(4001, cli.port)

    def test_add_good_key(self):
        self.conman.add_key('good')
        expected = self.good_dict
        actual = self.conman._conf['good']
        self.assertEqual(expected, actual)

    def test_add_bad_key(self):
        self.assertRaises(Exception, self.conman.add_key, 'no such key')

    def test_refresh(self):
        self.assertFalse('refresh_test' in self.conman._conf)

        # Insert a new key to etcd
        set_key(self.conman.client, 'refresh_test', dict(a='1'))

        # The new key should still not be visible by conman
        self.assertFalse('refresh_test' in self.conman._conf)

        # Refresh to get the new key
        self.conman.refresh('refresh_test')

        # The new key should now be visible by conman
        self.assertEqual(dict(a='1'), self.conman._conf['refresh_test'])

        # Change the key
        set_key(self.conman.client, 'refresh_test', dict(b='3'))

        # The previous value should still be visible by conman
        self.assertEqual(dict(a='1'), self.conman._conf['refresh_test'])

        # Refresh again
        self.conman.refresh('refresh_test')

        # The new value should now be visible by conman
        self.assertEqual(dict(b='3'), self.conman._conf['refresh_test'])

    def test_dictionary_access(self):
        self.conman.add_key('good')
        self.assertEqual(self.good_dict, self.conman['good'])
