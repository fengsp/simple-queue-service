# -*- coding: utf-8 -*-
"""
    sqs.client
    ~~~~~~~~~~

    A Kestrel client and one ext for Flask app.

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
from collections import defaultdict

from flask import g
from werkzeug.local import LocalProxy
import memcache


class Kestrel(object):
    """This is one Kestrel client. At the same time it acts as one Flask ext,
    Each app that want to use this class can simply do this:
        
        from flask import Flask
        app = Flask(__name__)
        Kestrel(app)

        queue = g.kestrel
        # queue = LocalProxy(lambda: g.kestrel)

    :param app: the Flask app object
    """

    #: default servers to connect to
    DEFAULT_SERVERS = ['127.0.0.1:22133']

    def __init__(self, app=None):
        self.app = app
        self.__memcache = None

        self.init_kestrel()

        if app is not None:
            self.init_app(app)

    def init_kestrel(self, app=None):
        """Config Kestrel with app.config"""
        if app:
            self.servers = app.config.get('kestrel_servers', DEFAULT_SERVERS)
        else:
            self.servers = DEFAULT_SERVERS
    
    def init_app(self, app):
        """Set up this instance for use with *app*"""
        self.app = app
        app.kestrel_instance = self
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['kestrel'] = self

        self.init_kestrel(app)

        # Using Kestrel with Flask
        def get_kestrel():
            client = getattr(g, '_kestrel_queue', None)
            if client is None:
                client = g._kestrel_queue = self.connect()
            return client
        def attach_kestrel():
            g.kestrel = LocalProxy(get_kestrel)
        app.before_request(attach_kestrel)
        def close_kestrel(exception):
            client = getattr(g, '_kestrel_queue', None)
            if client is not None:
                client.close()
        app.teardown_appcontext(close_kestrel)

    def connect(self):
        """Connect to the kestrel server. So basiclly you have to explicitly 
        connect before using the client."""
        return self

    def close(self):
        """Just close the connection."""
        pass
