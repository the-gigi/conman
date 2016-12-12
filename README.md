Conman
======
A Python configuration manager that handles multiple configuration files 
and distributed configuration via [etcd](https://coreos.com/etcd/).

If you want to use the distributed option you need to install etcd (duh!).

Conman was tested against etcd 2.2.5.

Supported File Formats
======================
Conman support YAML, JSON and INI file formats.

Usage
=====
See the tests directory for examples.

Article
=======
I wrote conman to support a [Dr. Dobbs](http://www.drdobbs.com/) article 
called [Program Configuration in Python](http://www.drdobbs.com/open-source/program-configuration-in-python/240169310).

In the article I go over conman's code and explain all the important parts.

Watch Feature
=============

A new feature that is not covered by the article is automatic watch changes 
for keys of EtcdConMan. When using this class you can provide a 
callback function that will be called whenever any value is 
added/removed/modifed under any key. 
