#!/usr/bin/env python
import psutil
import subprocess
import time
from conman.conman_etcd import thrice
from etcd3.exceptions import Etcd3Exception

etcd_process = None


def start_local_etcd_server():
    """Start etcd if not running already

    Note: this function is blocking
    """
    if is_local_etcd_running():
        return

    global etcd_process
    etcd_process = subprocess.Popen(
        '/usr/local/bin/etcd',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    # Wait for etcd process to start
    while not is_local_etcd_running():
        time.sleep(1)
    # wait a little longer to let etcd warm up
    time.sleep(2)


def is_local_etcd_running():
    etcd = None
    for p in psutil.process_iter():
        try:
            if p.name() == 'etcd' and p.status() != 'zombie':
                etcd = p
                break
        except psutil.ZombieProcess:
            pass

    if not etcd:
        return False

    return etcd.status() == 'running'


def kill_local_etcd_server():
    global etcd_process
    if etcd_process is not None:
        etcd_process.stdout.close()
        etcd_process.stderr.close()
        etcd_process.kill()
        try:
            etcd_process.wait(3)
        except psutil.TimeoutExpired:
            etcd_process.terminate()
        etcd_process = None

    if not is_local_etcd_running():
        return

    for p in psutil.process_iter():
        try:
            if p.name() == 'etcd' and p.status() != 'zombie':
                p.kill()
        except psutil.ZombieProcess:
            pass

    # Wait for 10 seconds for process to die
    for i in range(20):
        if not is_local_etcd_running():
            return

        time.sleep(0.5)

    # Server didn't die, just give up and raise an exception
    raise Exception('local etcd server is still running')


@thrice()
def set_key(client, key, values):
    """Insert a bunch of key value pairs to an etcd key using etcdctl.

    The values must be a dictionary, sub-keys will be created
    """
    delete_key(client, key)
    assert isinstance(values, dict)
    for name, value in values.items():
        k = '{0}/{1}'.format(key, name)
        if isinstance(value, dict):
            set_key(client, k, value)
        else:
            client.put(k, value)


@thrice()
def delete_key(client, key):
    """Delete a key if exists

    Ignore non-existing keys
    """
    try:
        client.delete_prefix(key)
    except Etcd3Exception:
        pass
    except Exception as e:
        # Ignore Raft internal errors that happen here sometimes
        if str(e) != 'Raft Internal Error : None':
            raise
