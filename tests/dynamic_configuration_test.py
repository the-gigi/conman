"""Demonstrate how to do dynamic configuration with conamn"""
import os
import time
from multiprocessing import Process
from unittest import TestCase

from conman.conman_etcd import ConManEtcd
from etcd_test_util import (start_local_etcd_server,
                            kill_local_etcd_server,
                            delete_key, set_key)
from tests.dyn_conf_program import Program


class DynamicConfigurationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        os.system('rm dyn_conf*.txt')
        kill_local_etcd_server()
        # Start local etcd server if not running
        start_local_etcd_server()

    @classmethod
    def tearDownClass(cls):
        try:
            kill_local_etcd_server()
        except:  # noqa
            pass

    def setUp(self):
        self.conman = ConManEtcd()
        self.cli = self.conman.client
        self.key = 'dyn_conf'
        set_key(self.cli, self.key, dict(a='1', b='Yeah, it works!!!'))

    def tearDown(self):
        self.conman.stop_watchers()
        delete_key(self.conman.client, self.key)

    def test_dynamic_configuration(self):
        # Launch 3 programs
        count = 3
        programs = []
        filenames = [os.path.abspath('dyn_conf_{}.txt'.format(i)) for i
                     in range(count)]
        for i in range(count):
            p = Process(target=Program, kwargs=dict(key='dyn_conf',
                                                    filename=filenames[i]))
            programs.append(p)
            p.start()

        cli = self.conman.client

        # Let the programs start and connect to etcd
        time.sleep(3)

        # Update the configuration
        cli.write(self.key + '/c', value=dict(d=6))

        # Get the output from all the programs
        output = [open(f).read() for f in filenames]
        for i in range(5):
            if output[0] == '':
                time.sleep(1)
            output = [open(f).read() for f in filenames]

        expected = \
            ["key: /dyn_conf/c, action: set, value: {'d': 6}\n"] * count
        self.assertEquals(expected, output)

        # Tell all programs to stop via dynamic configuration
        cli.write(self.key + '/stop', value=1)

        for p in programs:
            p.join()

        print 'Done.'
