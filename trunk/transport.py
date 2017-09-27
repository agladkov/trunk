# -*- coding: utf-8  -*-
from kombu.transport import virtual

from trunk.queue import PGQueue
from trunk.utils import build_dsn

import logging

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_fmt, level=logging.INFO)
logger = logging.getLogger(__name__)


class Channel(virtual.Channel):
    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)
        parts = self.connection.client
        dsn = build_dsn(scheme='postgres', hostname=parts.hostname,
                        port=parts.port, path=parts.virtual_host,
                        username=parts.userid, password=parts.password)
        self.queue = PGQueue(dsn)

    def _new_queue(self, queue, **kwargs):
        self.queue.create(queue)

    def _get(self, queue, timeout=None):
        _, message = self.queue.get_nowait(queue)
        return message

    def _put(self, queue, message, **kwargs):
        self.queue.put(queue, message)

    def _purge(self, queue):
        return self.queue.purge(queue)

    def close(self):
        super(Channel, self).close()
        self.queue.close()


class Transport(virtual.Transport):
    Channel = Channel

    default_port = 5432

    driver_type = 'postgres'
    driver_name = 'postgres'


transport = Transport  # hack to get kombu to load the class
