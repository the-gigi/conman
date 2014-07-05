import os
from unittest import TestCase
from conman.conman_etcd import ConManEtcd
from etcd_test_util import start_local_etcd_server, kill_local_etcd_server, \
    add_key


class ConManEtcdTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Start local etcd server if not running
        start_local_etcd_server()

        # Add good key
        cls.good_dict = dict(a='1', b='Yeah, it works!!!')
        add_key('good', cls.good_dict)

    @classmethod
    def tearDownClass(cls):
        try:
            kill_local_etcd_server()
        except:  # noqa
            pass

    def setUp(self):
        self.conman = ConManEtcd()

    def tearDown(self):
        pass

    def test_initialization(self):
        cli = self.conman.client
        self.assertEqual('http://127.0.0.1:4001', cli.base_uri)
        self.assertEqual(['http://127.0.0.1:4001'], cli.machines)
        self.assertEqual('127.0.0.1', cli.host)
        self.assertEqual(4001, cli.port)

    def test_add_good_key(self):
        self.conman.add_key('good')
        expected = self.good_dict
        actual = self.conman.keys['good']
        self.assertEqual(expected, actual)

    def test_add_bad_key(self):
        self.assertRaises(Exception, self.conman.add_key, 'no such key')

    def test_refresh(self):
        pass

    def test_get_key(self):
        pass
