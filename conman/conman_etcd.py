"""A configuration management class built on top of etcd

See:  http://python-etcd.readthedocs.org/

It provides a read-only access and just exposes a nested dict
"""
import functools
import time
from threading import Thread

import etcd
from conman.conman_base import ConManBase


def thrice(delay=0.5):
    """This decorator tries failed operations 3 times before it gives up

    The delay determines how long to wait between tries (in seconds)
    """

    def decorated(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            for i in xrange(3):
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
                 port=4001,
                 srv_domain=None,
                 version_prefix='/v2',
                 read_timeout=60,
                 allow_redirect=True,
                 protocol='http',
                 cert=None,
                 ca_cert=None,
                 username=None,
                 password=None,
                 allow_reconnect=False,
                 use_proxies=False,
                 expected_cluster_id=None,
                 per_host_pool_size=10,
                 on_change=lambda k, a, v: None,
                 watch_timeout=30):
        ConManBase.__init__(self)
        self.on_change = on_change
        self.watch_timeout = watch_timeout
        self.stop_watching = False

        self.client = etcd.Client(
            host=host,
            port=port,
            srv_domain=srv_domain,
            version_prefix=version_prefix,
            read_timeout=read_timeout,
            allow_redirect=allow_redirect,
            protocol=protocol,
            cert=cert,
            ca_cert=ca_cert,
            username=username,
            password=password,
            allow_reconnect=allow_reconnect,
            use_proxies=use_proxies,
            expected_cluster_id=expected_cluster_id,
            per_host_pool_size=per_host_pool_size)

    def _add_key_recursively(self, target, key, etcd_result):
        if key.startswith('/'):
            key = key[1:]
        if etcd_result.value:
            target[key] = etcd_result.value
        else:
            target[key] = {}
            target = target[key]
            for c in etcd_result.leaves:
                # If there are no children it returns the etcd_result itself
                if c == etcd_result:
                    continue
                k = c.key.split('/')[-1]
                self._add_key_recursively(target, k, c)

    def watch(self, key):
        """Watch a key in a thread"""

        def watch_key():
            while not self.stop_watching:
                try:
                    result = self.client.watch(key,
                                               recursive=True,
                                               timeout=self.watch_timeout)
                    try:
                        self.on_change(result.key,
                                       result.action,
                                       result.value)
                    except Exception as e:  # noqa
                        pass
                except etcd.EtcdWatchTimedOut as e:  # noqa
                    pass

        if not self.stop_watching:
            Thread(target=watch_key).start()

    def add_key(self, key, watch=True):
        """Add a key to managed etcd keys and store its data

        :param str key: the etcd path
        :param bool watch: determine if need to watch the key

        When a key is added all its data is stored as a dict
        """
        etcd_result = self.client.read(key, recursive=True, sorted=True)
        self._add_key_recursively(self._conf, key, etcd_result)
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
            self.add_key(k, watch=False)

    def stop_watchers(self):
        """All watching threads will stop soon"""
        self.stop_watching = True
