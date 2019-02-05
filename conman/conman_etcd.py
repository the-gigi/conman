"""A configuration management class built on top of etcd

See:  http://python-etcd.readthedocs.org/

It provides a read-only access and just exposes a nested dict
"""
import functools
import time
import etcd3
from conman.conman_base import ConManBase


def thrice(delay=0.5):
    """This decorator tries failed operations 3 times before it gives up

    The delay determines how long to wait between tries (in seconds)
    """

    def decorated(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            for i in range(3):
                try:
                    return f(*args, **kwargs)
                except Exception:
                    if i == 2:
                        raise
                    time.sleep(delay)

        return wrapped

    return decorated


class ConManEtcd(ConManBase):
    def __init__(self,
                 host='127.0.0.1',
                 port=2379,
                 ca_cert=None,
                 cert_key=None,
                 cert_cert=None,
                 timeout=None,
                 user=None,
                 password=None,
                 grpc_options=None,
                 on_change=lambda e: None):
        ConManBase.__init__(self)
        self.on_change = on_change
        self.client = etcd3.client(
            host=host,
            port=port,
            ca_cert=ca_cert,
            cert_key=cert_key,
            cert_cert=cert_cert,
            timeout=timeout,
            user=user,
            password=password,
            grpc_options=grpc_options,
        )

    def _add_key_recursively(self, etcd_result):
        ok = False
        target = self._conf
        for x in etcd_result:
            ok = True
            value = x[0].decode()
            key = x[1].key.decode()
            components = key.split('/')
            t = target
            for c in components[:-1]:
                if c not in t:
                    t[c] = {}
                t = t[c]
            t[components[-1]] = value
        if not ok:
            raise Exception('Empty result')

    def watch(self, key):
        watch_id = self.client.add_watch_callback(key, self.on_change)
        return watch_id

    def watch_prefix(self, key):
        return self.client.watch_prefix(key)

    def cancel(self, watch_id):
        self.client.cancel_watch(watch_id)

    def add_key(self, key, watch=False):
        """Add a key to managed etcd keys and store its data

        :param str key: the etcd path
        :param bool watch: determine if need to watch the key

        When a key is added all its data is stored as a dict
        """
        etcd_result = self.client.get_prefix(key, sort_order='ascend')
        self._add_key_recursively(etcd_result)
        if watch:
            self.watch(key)

    def refresh(self, key=None):
        """Refresh an existing key or all keys

        :param key: the key to refresh (if None refresh all keys)

        If the key parameter doesn't exist an exception will be raised.
        No need to watch again the conf keys.
        """
        keys = [key] if key else self._conf.keys()
        for k in keys:
            if k in self._conf:
                del self._conf[k]
            self.add_key(k, watch=False)
