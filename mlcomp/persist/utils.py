# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import threading
from contextlib import contextmanager
from logging import getLogger

__all__ = ['duplicate_console_output', 'BackgroundWorker']


@contextmanager
def duplicate_console_output(path, stderr=False, append=False):
    """Copy the STDOUT and STDERR to both the console and a file.

    Parameters
    ----------
    path : str
        Path of the output file.

    stderr : bool
        The console output, including STDOUT and STDERR, would be aggregated,
        thus there will only be one console output within the open context.

        If set to False, will aggregate both STDOUT and STDERR into STDOUT.
        Otherwise will aggregate both STDOUT and STDERR into STDERR.

    append : bool
        Whether or not to open the output file in append mode?
    """
    # flush the original stdout and stderr
    sys.stdout.flush()
    sys.stderr.flush()

    # determine the arguments of calling `_tee.py`
    args = [
        sys.executable,
        '-u',
        os.path.abspath(os.path.join(os.path.dirname(__file__), '_tee.py')),
        '--file',
        os.path.abspath(path),
    ]
    if stderr:
        args.append('--stderr')
    if append:
        args.append('--append')

    # open the subprocess and get its stdin file descriptor
    proc = subprocess.Popen(args, stdin=subprocess.PIPE)
    proc_fd = proc.stdin.fileno()

    # get the stdout and stderr file descriptors
    stdout_fd = sys.stdout.fileno()
    stderr_fd = sys.stderr.fileno()

    # the duplicated stdout and stderr file descriptors
    stdout_fd2 = None
    stderr_fd2 = None

    # now redirect the STDOUT and STDERR
    try:
        stdout_fd2 = os.dup(stdout_fd)
        os.dup2(proc_fd, stdout_fd)
        stderr_fd2 = os.dup(stderr_fd)
        os.dup2(proc_fd, stderr_fd)
        yield

    finally:
        # flush the stdout and stderr before cancelling redirection.
        try:
            sys.stdout.flush()
        except Exception:
            getLogger(__name__).debug('failed to flush stdout', exc_info=True)
        try:
            sys.stderr.flush()
        except Exception:
            getLogger(__name__).debug('failed to flush stderr', exc_info=True)

        # recover the stdout and stderr file descriptors
        if stderr_fd2 is not None:
            os.dup2(stderr_fd2, stderr_fd)
            os.close(stderr_fd2)
        if stdout_fd2 is not None:
            os.dup2(stdout_fd2, stdout_fd)
            os.close(stdout_fd2)

        # close the stdin of child process, so that it will receive an
        # error on os.read(stdin), thus exit.
        proc.stdin.close()
        try:
            os.close(proc_fd)
        except Exception:
            getLogger(__name__).debug('failed to close proc_fd', exc_info=True)

        # wait the child process to exit.
        status = proc.wait()
        if status != 0:
            getLogger(__name__).warning(
                'Exit code of tee process %d != 0.', status, exc_info=True)


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
        self._stop_sem = None   # type: threading.Semaphore

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
                if self._stop_sem.acquire(timeout=self.sleep_seconds):
                    break
        finally:
            self._stopped = True

    def start(self):
        # initialize synchronization objects
        self._stopped = False
        self._start_sem = threading.Semaphore(0)
        self._stop_sem = threading.Semaphore(0)
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
            self._stop_sem.release()

            # wait for the worker thread to exit
            self._worker.join()
            self._worker = None
