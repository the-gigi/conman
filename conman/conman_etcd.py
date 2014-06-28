"""A configuration management class built on top of etcd

See:  http://python-etcd.readthedocs.org/

It provides a read-only access and just exposes a nested dict
"""
import etcd


class ConManEtcd(object):
    def __init__(self, host='127.0.0.1', port=4003, allow_reconnect=True):
        self.client = etcd.Client(
            host=host,
            port=port,
            allow_reconnect=allow_reconnect)

        self.keys = {}

    def add_key(self, key, refresh_in_seconds=None):
        """Add a key to managed etcd keys and store its data

        :param key: the etcd path
        :param refresh_in_seconds: wait time between refreshes


        When a key is added all its data is stored as a dict. It will be
        fetched again every <refresh_in_seconds>. If the refresh period is None
        no automatic refresh occurs.
        """

    def refresh(self, key=None):
        """
        :param key: the key to refresh (if None refresh all keys)
        """

    def _get_key(self, key):
        """Get all the data stored under an etcd key and return it as a dict

        :param key: the etcd path to get
        """
