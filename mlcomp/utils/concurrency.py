# -*- coding: utf-8 -*-
import threading
from logging import getLogger

__all__ = ['BackgroundWorker']


class BackgroundWorker(object):
    """Background worker that executes some action periodically.

    To tell whether or not a thread actually starts or not, one has to
    create a semaphore so as to wait for the thread to actually show up.
    Also, if one wants to gracefully interrupt a sleeping thread, he must
    have another semaphore to notify the sleeping thread.

    Parameters
    ----------
    action : () -> None
        The action to be executed periodically.

    sleep_seconds : float
        Number of seconds to sleep between two periodical execution.

    name : str
        Optional name of this background worker.

    stop_on_error : bool
        Whether or not to stop the thread on error?  Default is False.
    """

    def __init__(self, action, sleep_seconds, name=None, stop_on_error=False):
        self.action = action
        self.sleep_seconds = sleep_seconds
        self.name = name
        self.stop_on_error = stop_on_error
        self._stopped = False
        self._worker = None     # type: threading.Thread
        self._start_sem = None  # type: threading.Semaphore
        self._stop_cond = None  # type: threading.Condition

    def _thread_run(self):
        self._stopped = False
        # notify the `open()` method that we've successfully started.
        self._start_sem.release()

        # dump the running flag every per `interval` until stopped.
        try:
            while not self._stopped:
                try:
                    self.action()
                except Exception:
                    if self.name:
                        getLogger(__name__).warning(
                            'background worker [%s]: failed to execute.',
                            self.name, exc_info=True
                        )
                    else:
                        getLogger(__name__).warning(
                            'background worker failed to execute.',
                            exc_info=True
                        )
                    if self.stop_on_error:
                        break

                # sleep by using the condition, so that we can interrupt
                # it gracefully.
                if not self._stopped:
                    with self._stop_cond:
                        self._stop_cond.wait(timeout=self.sleep_seconds)
        finally:
            self._stopped = True

    def start(self):
        # initialize synchronization objects
        self._stopped = False
        self._start_sem = threading.Semaphore(0)
        self._stop_cond = threading.Condition()
        # create the worker thread
        self._worker = threading.Thread(target=self._thread_run)
        self._worker.daemon = True
        self._worker.start()
        # wait for the worker to actually start
        self._start_sem.acquire()

    def stop(self):
        if not self._stopped:
            # notify the worker thread to exit
            self._stopped = True
            with self._stop_cond:
                self._stop_cond.notify_all()

            # wait for the worker thread to exit
            self._worker.join()
            self._worker = None
