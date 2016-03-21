from collections import defaultdict
from functools import partial
from unittest import TestCase

import time

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
        delete_key(self.conman.client, 'watch_test')
        self.conman.stop_watchers()

    def test_initialization(self):
        cli = self.conman.client
        self.assertEqual('http://127.0.0.1:4001', cli.base_uri)
        self.assertEqual('127.0.0.1', cli.host)
        self.assertEqual(4001, cli.port)

    def test_add_good_key(self):
        self.conman.add_key('good')
        expected = self.good_dict
        actual = self.conman['good']
        self.assertEqual(expected, actual)

    def test_add_bad_key(self):
        self.assertRaises(Exception, self.conman.add_key, 'no such key')

    def test_refresh(self):
        self.assertFalse('refresh_test' in self.conman)

        # Insert a new key to etcd
        set_key(self.conman.client, 'refresh_test', dict(a='1'))

        # The new key should still not be visible by conman
        self.assertFalse('refresh_test' in self.conman)

        # Refresh to get the new key
        self.conman.refresh('refresh_test')

        # The new key should now be visible by conman
        self.assertEqual(dict(a='1'), self.conman['refresh_test'])

        # Change the key
        set_key(self.conman.client, 'refresh_test', dict(b='3'))

        # The previous value should still be visible by conman
        self.assertEqual(dict(a='1'), self.conman['refresh_test'])

        # Refresh again
        self.conman.refresh('refresh_test')

        # The new value should now be visible by conman
        self.assertEqual(dict(b='3'), self.conman['refresh_test'])

    def test_dictionary_access(self):
        self.conman.add_key('good')
        self.assertEqual(self.good_dict, self.conman['good'])

    def test_watch_existing_key(self):
        def on_change(change_dict, key, action, value):
            change_dict[key].append((action, value))

        change_dict = defaultdict(list)
        self.assertFalse('watch_test' in self.conman)

        # Insert a new key to etcd
        self.conman.client.write('watch_test/a', 1)

        # The new key should still not be visible by conman
        self.assertFalse('watch_test' in self.conman)

        # Refresh to get the new key
        self.conman.refresh('watch_test')

        # The new key should now be visible by conman
        self.assertEqual(dict(a='1'), self.conman['watch_test'])

        # Set the on_change() callback of conman (normally at construction)
        on_change = partial(on_change, change_dict)
        self.conman.on_change = on_change
        self.conman.watch('watch_test')

        # Change the key
        self.conman.client.write('watch_test/b', '3')

        # The previous value should still be visible by conman
        self.assertEqual(dict(a='1'), self.conman['watch_test'])

        # Wait for the change callback to detect the change
        for i in range(3):
            if change_dict:
                break
            time.sleep(1)

        expected = {'/watch_test/b':[('set', '3')]}
        actual = dict(change_dict)
        self.assertEquals(expected, actual)

        # Refresh again
        self.conman.refresh('watch_test')

        # The new value should now be visible by conman
        self.assertEqual(dict(a='1', b='3'), self.conman['watch_test'])
