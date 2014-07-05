#!/usr/bin/env python
import os
import subprocess
import time
import psutil


def start_local_etcd_server():
    """Start etcd if not running already

    Note: this function is blocking
    """
    if is_local_etcd_running():
        return

    p = subprocess.Popen('etcd',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    # Wait for etcd process to start
    while not is_local_etcd_running():
        time.sleep(0.1)

    print 'etcd running...'


def is_local_etcd_running():
    # Get non-zombie process names
    names = [p.name for p in psutil.process_iter() if p.status != 'zombie']
    if not 'etcd' in names:
        return False

    # Sleep a little to make sure it can respond
    time.sleep(0.5)
    return True


def kill_local_etcd_server():
    if not is_local_etcd_running():
        return

    for p in psutil.process_iter():
        if p.name == 'etcd' and p.status != 'zombie':
            p.kill()

    # Wait for 10 seconds for process to die
    for i in range(20):
        if not is_local_etcd_running():
            return

        time.sleep(0.5)

    # Server didn't die, just give up and raise an exception
    raise Exception('local etcd server is still running')


def add_key(key, values):
    """Add a bunch of key value pairs to an etcd key using etcdctl.

    The values must be a dictionary, sub-keys will be created
    """
    assert isinstance(values, dict)
    for name, value in values.iteritems():
        if isinstance(value, str):
            value = "'{0}'".format(value)
        os.system('etcdctl set {0}/{1} {2}'.format(key, name, value))





