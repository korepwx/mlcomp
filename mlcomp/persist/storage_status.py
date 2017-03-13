# -*- coding: utf-8 -*-
import codecs
import json
import os
import socket

import time

__all__ = ['StorageRunningStatus']


class StorageRunningStatus(object):
    """Storage running status.

    Parameters
    ----------
    pid : int
        The running process id.

    hostname : str
        The hostname of the running process.

    start_time : float
        The timestamp when the running process started.

    active_time : float
        The timestamp of the last running process activity.
    """

    __repr_attributes__ = ('pid', 'hostname', 'start_time', 'active_time')

    def __init__(self, pid, hostname, start_time, active_time):
        self.pid = pid
        self.hostname = hostname
        self.start_time = start_time
        self.active_time = active_time

    def __repr__(self):
        attrs = ','.join(
            '%s=%r' % (k, getattr(self, k))
            for k in self.__repr_attributes__
        )
        return 'StorageRunningStatus(%s)' % attrs

    def __eq__(self, other):
        if isinstance(other, StorageRunningStatus):
            return self.to_dict() == other.to_dict()
        return False

    def to_dict(self):
        return {
            'pid': self.pid,
            'hostname': self.hostname,
            'start_time': self.start_time,
            'active_time': self.active_time
        }

    @classmethod
    def load_file(cls, status_file):
        """Load the running status from file.

        Parameters
        ----------
        status_file : str
            The running status file.

        Returns
        -------
        StorageRunningStatus | None
            The loaded running status, or None if the status file
            does not exist.
        """
        with codecs.open(status_file, 'rb', 'utf-8') as f:
            values = json.load(f)
            return StorageRunningStatus(
                pid=values.get('pid'),
                hostname=values.get('hostname'),
                start_time=values.get('start_time'),
                active_time=values.get('active_time')
            )

    @classmethod
    def generate(cls):
        """Generate a new running status."""
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = None
        return StorageRunningStatus(
            pid=os.getpid(),
            hostname=hostname,
            start_time=time.time(),
            active_time=time.time()
        )

    def save_file(self, status_file):
        """Save the running status to file."""
        with codecs.open(status_file, 'wb', 'utf-8') as f:
            json.dump(self.to_dict(), f)
