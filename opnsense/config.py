# -*- encoding: utf-8 -*-

"""

This wrapper will first look for direct instanciation parameters then
``OPNSENSE_KEY``, ``OPNSENSE_SECRET`` environment variables.
If either of these parameter is not provided, it will look for a
configuration file of the form:

.. code:: ini

    [default]
    ; general configuration: default endpoint
    key=dzadzadzadaz
    secret=dazdzadzadzadza


The client will successively attempt to locate this configuration file in

1. Current working directory: ``./opnsense.conf``
2. Current user's home directory ``~/.opnsense.conf``
3. System wide configuration ``/etc/opnsense.conf``

This lookup mechanism makes it easy to overload credentials for a specific
project or user.
"""

import os

try:
    from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
except ImportError:  # pragma: no cover
    # Python 3
    from configparser import RawConfigParser, NoSectionError, NoOptionError

__all__ = ['config']

#: Locations where to look for configuration file by *increasing* priority
CONFIG_PATH = [
    '/etc/opnsense.conf',
    os.path.expanduser('~/.opnsense.conf'),
    os.path.realpath('./opnsense.conf'),
]


class ConfigurationManager(object):
    '''
    Application wide configuration manager
    '''
    def __init__(self):
        '''
        Create a config parser and load config from environment.
        '''
        # create config parser
        self.config = RawConfigParser()
        self.config.read(CONFIG_PATH)

    def get(self, section, name):
        '''
        Load parameter ``name`` from configuration, respecting priority order.
        '''
        # 1/ try env
        try:
            return os.environ['OPNSENSE_'+name.upper()]
        except KeyError:
            pass

        # 2/ try from specified section/endpoint
        try:
            return self.config.get(section, name)
        except (NoSectionError, NoOptionError):
            pass

        # not found, sorry
        return None

    def read(self, config_file):
        # Read an other config file
        self.config.read(config_file)


#: System wide instance :py:class:`ConfigurationManager` instance
config = ConfigurationManager()
