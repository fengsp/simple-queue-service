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
    """This is one Flask extension for Kestrel Client. 
    Each app that want to use this ext can simply do this::
    
        from flask import Flask
        app = Flask(__name__)
        kestrel = Kestrel(app)
        queue = kestrel.queue

    :param app: the Flask app object
    """
    def __init__(self, app):
        """Init the kestrel ext.

        :param app: The Flask app.
        """
        self.app = app
        self.kestrel = None
        self.init_app(app)
    
    def init_app(self, app):
        """Set up this instance for use with *app*"""
        app.kestrel_instance = self
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['kestrel'] = self
        
        def get_kestrel():
            client = getattr(g, '_kestrel_queue', None)
            if client is None:
                client = g._kestrel_queue = \
                         KestrelClient(app.config['KESTREL_SERVERS'])
            return client
        kestrel = LocalProxy(get_kestrel)

        def close_kestrel(exception):
            client = getattr(g, '_kestrel_queue', None)
            if client is not None:
                g._kestrel_queue = None
                client.close()
        app.teardown_appcontext(close_kestrel)
        
        self.kestrel = kestrel
    
    @property
    def queue(self):
        return self.kestrel


class KestrelClient(object):
    """This is one Kestrel client. 

    :param app: the Flask app object
    """

    #: default servers to connect to
    DEFAULT_SERVERS = ['127.0.0.1:22133']

    def __init__(self, servers=None):
        """Init the kestrel client.

        :param servers: A list of the kestrel servers.
        """
        self.servers = servers if servers else self.DEFAULT_SERVERS
        self.connect()

    def connect(self):
        """Connect to the kestrel server. """
        self.__memcache = KestrelMemcacheClient(servers=self.servers)
        return self

    def get(self, queue, timeout=None):
        """Get a msg off the specific queue.

        :param queue: The queue you want to dequeue
        :param timeout: The time to wait for a msg if none are on the queue.
            (milliseconds)
        :return: The msg
        """
        cmd = '%s' % queue
        if timeout is not None:
            cmd = '%s/t=%d' % (cmd, timeout)
        return self.__memcache.get('%s' % cmd)
        
    def put(self, queue, data, expire=None):
        """Put a msg into the specific queue.

        :param queue: The queue you want to enqueue
        :param data: The msg (just support string type)
        :param expire: The expiration time of the msg
        :return: `True` or `False`
        """
        if not isinstance(data, str):
            raise TypeError('data must be of string type')
        if expire is None:
            expire = 0

        ret = self.__memcache.set(queue, data, expire)

        if ret == 0:
            return False
        return False

    def delete(self, queue):
        """Delete the specific queue from the kestrel server

        :return: `True` or `False`
        """
        ret = self.__memcache.delete(queue)
        if ret == 0:
            return False
        return True

    def next(self, queue, timeout=None):
        """Get a msg off the specific queue (Reliable)

        :param queue: The queue you want to dequeue
        :param timeout: The time to wait for a msg if none are on the queue.
            (milliseconds)
        :return: The msg
        """
        cmd = '%s/close' % queue
        if timeout is not None:
            cmd = '%s/t=%d' % (cmd, timeout)
        return self.__memcache.get('%s/open' % cmd)

    def peek(self, queue, timeout=None):
        """return the first available item from the specific queue, but not 
        remove it

        :param queue: The queue you want to have a peek
        :param timeout: The time to wait for a msg if none are on the queue.
            (milliseconds)
        :return: The msg
        """
        cmd = '%s/peek' % queue
        if timeout is not None:
            cmd = '%s/t=%d' % (cmd, timeout)
        return self.__memcache.get(cmd)

    def abort(self, queue):
        """Abort a read

        :param queue: The queue you want to abort
        :return: `True`
        """
        self.__memcache.get('%s/abort' % queue)
        return True

    def finish(self, queue):
        """Close a open request on one specific queue

        :param queue: The queue you want to close the open request
        :return: `True`
        """
        self.__memcache.get('%s/close' % queue)
        return True
    
    def flush(self, queue):
        """Discard all msgs remaining in the specific queue

        :param queue: The queue you want to clear out
        :return: `True`
        """
        self.__memcache.flush(queue)
        return True

    def flush_all(self):
        """Discard all msgs remaining in all queues

        :return: `True`
        """
        self.__memcache.flush_all()
        return True

    def reload(self):
        """Reload the config file and reconfigure all queues

        :return: `True`
        """
        self.__memcache.reload()
        return True

    def raw_stats(self, dump=False):
        """Get raw stats

        :param dump: Set to `True` to get `DUMP_STATS` COMMAND result, so you
                     can get server stats in a more readable style. Default to                      
                     `False` to get `STATS` COMMAND result, and you get server 
                     stats i memcache style
        :return: The raw stats
        """
        if dump is True:
            return self.__memcache.dump_stats()
        return self.__memcache.get_stats()

    def stats(self):
        """Get server stats (Python dict)

        :return: The server stats dict
        """
        server = None
        s_stats = {}
        q_stats = {}

        for server, stats in self.raw_stats():
            server = server.split(' ', 1)[0]
            for name, stat in stats.iteritems():
                if not name.startswith('queue_'):
                    try:
                        s_stats[name] = long(stat)
                    except ValueError:
                        s_stats[name] = stat
        
        for name, stats in re.findall(
                           r'queue \'(?P<name>.*?)\' \{(?P<stats>.*?)\}', 
                           self.raw_stats(True), re.DOTALL):
            _stats = {}
            for stat in [stat.strip() for stat in stats.split('\n')]:
                if stat.count('='):
                    key, value = stat.split('=')
                    _stats[key] = long(value)
            q_stats[name] = _stats

        if server is None:
            return {}
        return dict([('server', s_stats), ('queues', q_stats)])

    def shutdown(self):
        """Cleanly shutdown the server and exit
        """
        self.__memcache.shutdown()

    def version(self):
        """Get the version of the kestrel server

        :return: The kestrel server version
        """
        return self.__memcache.version()

    def close(self):
        """Just close the connection."""
        self.__memcache.disconnect_all()
        return True


class KestrelMemcacheClient(memcache.Client):
    """Kestrel Memcache Client.

    Adding commands: RELOAD, FLUSH, DUMP_STATS, SHUTDOWN, VERSION
    """

    def reload(self):
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('RELOAD')
            s.expect('OK')

    def flush(self, key):
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('FLUSH %s' % (key))
            s.expect('OK')

    def dump_stats(self):
        return self.__read_cmd('DUMP_STATS')

    def shutdown(self):
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('SHUTDOWN')

    def version(self):
        data = []
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('VERSION')
            data.append(s.readline())

        return '\n'.join(data).split(' ', 1)[1]

    def __read_cmd(self, cmd):
        data = []
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd(cmd)
            data.append(self.__read_string(s))

        return '\n'.join(data)

    def __read_string(self, s):
        data = []
        while True:
            line = s.readline()
            if not line or line.strip() == 'END': break
            data.append(line)
        return '\n'.join(data)
