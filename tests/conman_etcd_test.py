import os
import sys
import time
from collections import defaultdict
from threading import Thread

from conman.conman_etcd import ConManEtcd
from conman.etcd_test_util import (start_local_etcd_server,
                                   kill_local_etcd_server,
                                   set_key,
                                   delete_key)
from functools import partial
from unittest import TestCase


class ConManEtcdTest(TestCase):
    @classmethod
    def setUpClass(cls):
        kill_local_etcd_server()
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
        cli = self.conman.client
        delete_key(cli, 'good')
        delete_key(cli, 'refresh_test')
        delete_key(cli, 'watch_test')
        cli.close()

    def test_initialization(self):
        cli = self.conman.client
        self.assertEqual('127.0.0.1:2379', cli._url)

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
        def on_change(change_dict, event):
            change_dict[event.key].append((type(event).__name__, event.value))

        change_dict = defaultdict(list)
        self.assertFalse('watch_test' in self.conman)

        # Insert a new key to etcd
        self.conman.client.put('watch_test/a', '1')

        # The new key should still not be visible by conman
        self.assertFalse('watch_test' in self.conman)

        # Refresh to get the new key
        self.conman.refresh('watch_test')

        # The new key should now be visible by conman
        self.assertEqual(dict(a='1'), self.conman['watch_test'])

        # Set the on_change() callback of conman (normally at construction)
        on_change = partial(on_change, change_dict)
        self.conman.on_change = on_change
        watch_id = None
        try:
            watch_id = self.conman.watch('watch_test/b')

            # Change the key
            self.conman.client.put('watch_test/b', '3')

            # The previous value should still be visible by conman
            self.assertEqual(dict(a='1'), self.conman['watch_test'])

            # Wait for the change callback to detect the change
            for i in range(3):
                if change_dict:
                    break
                time.sleep(1)

            expected = {b'watch_test/b': [('PutEvent', b'3')]}
            actual = dict(change_dict)
            self.assertEqual(expected, actual)

            # Refresh again
            self.conman.refresh('watch_test')

            # The new value should now be visible by conman
            self.assertEqual(dict(a='1', b='3'), self.conman['watch_test'])
        finally:
            if watch_id is not None:
                self.conman.cancel(watch_id)

    def test_watch_prefix(self):
        all_events = []

        def read_events_in_thread():
            with open(os.devnull, 'w') as f:
                sys.stdout = f
                sys.stderr = f
                events, cancel = self.conman.watch_prefix('watch_prefix_test')
                for event in events:
                    k = event.key.decode()
                    v = event.value.decode()
                    s = f'{k}: {v}'
                    all_events.append(s)
                    if v == 'stop':
                        cancel()

        t = Thread(target=read_events_in_thread)
        t.start()

        # Insert a new key to etcd
        self.conman.client.put('watch_prefix_test/a', '1')
        self.conman.client.put('watch_prefix_test/b', '2')
        time.sleep(1)
        self.conman.client.put('watch_prefix_test', 'stop')

        t.join()

        expected = [
            'watch_prefix_test/a: 1',
            'watch_prefix_test/b: 2',
            'watch_prefix_test: stop'
        ]
        self.assertEqual(expected, all_events)
