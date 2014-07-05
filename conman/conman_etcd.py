"""A configuration management class built on top of etcd

See:  http://python-etcd.readthedocs.org/

It provides a read-only access and just exposes a nested dict
"""
import etcd


class ConManEtcd(object):
    def __init__(self, host='127.0.0.1', port=4001, allow_reconnect=True):
        self.client = etcd.Client(
            host=host,
            port=port,
            allow_reconnect=allow_reconnect)

        self.keys = {}

    def _add_key_recursively(self, target, key, etcd_result):
        if key.startswith('/'):
            key = key[1:]
        if etcd_result.value:
            target[key] = etcd_result.value
        else:
            target[key] = {}
            target = target[key]
            for c in etcd_result.children:
                k = c.key.split('/')[-1]
                self._add_key_recursively(target, k, c)

    def add_key(self, key, refresh_in_seconds=None):
        """Add a key to managed etcd keys and store its data

        :param key: the etcd path
        :param refresh_in_seconds: wait time between refreshes


        When a key is added all its data is stored as a dict. It will be
        fetched again every <refresh_in_seconds>. If the refresh period is None
        no automatic refresh occurs.
        """
        etcd_result = self.client.read(key, recursive=True, sorted=True)
        self._add_key_recursively(self.keys, key, etcd_result)

    def refresh(self, key=None):
        """
        :param key: the key to refresh (if None refresh all keys)
        """

    def _get_key(self, key):
        """Get all the data stored under an etcd key and return it as a dict

        :param key: the etcd path to get
        """
        if key not in self.keys:
            return None
