Conman
======
A Python configuration manager that handles multiple configuration files 
and distributed configuration via [etcd](https://coreos.com/etcd/).

If you want to use the distributed option you need to install etcd (duh!).

Conman was tested against etcd 3.5

Supported File Formats
======================
Conman support YAML, JSON and INI file formats.


Requirements
============
For using etcd and/or running its tests you need to have etcd installed at `/usr/local/bin/etcd`

Check out installation options here: `https://github.com/etcd-io/etcd#getting-etcd`

Usage
=====
See the tests directory for examples.

Testing
=======

I use [tox](https://tox.readthedocs.io) for testing

```
$ pip install tox
$ tox
```


Article
=================
I wrote conman to support a [Dr. Dobbs](http://www.drdobbs.com/) article 
called [Program Configuration in Python](http://www.drdobbs.com/open-source/program-configuration-in-python/240169310).

In the article I go over conman's code and explain all the important parts.


Watch Feature
=============

A new feature that is not covered by the original article is automatic watch changes
for keys of EtcdConMan. When using this class you can provide a 
callback function that will be called whenever any value is 
added/removed/modifed under any key.

I wrote another article that covers it too on compose.io:

[Building a dynamic configuration service with Etcd and Python](https://www.compose.com/articles/building-a-dynamic-configuration-service-with-etcd-and-python/)
