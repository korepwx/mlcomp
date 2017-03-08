#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This file implements the `tee` command of Linux system, which copies
whatever it receives from STDIN to both STDOUT and some external file.
"""
import getopt
import os
import signal
import sys

BUFLEN = 8192


def disable_keyboard_interrupt(signal, frame):
    """
    Capture Ctrl+C so that keyboard interrupt of parent process will not
    interrupt this tee program unexpectedly.
    """

signal.signal(signal.SIGINT, disable_keyboard_interrupt)

# parse the arguments
is_stderr = False
is_append = False
output_target = None
opts, args = getopt.getopt(sys.argv[1:], 'f:ea', ['stderr', 'file=', 'append'])
for o, v in opts:
    if o in ('-f', '--file'):
        output_target = v
    elif o in ('-e', '--stderr'):
        is_stderr = True
    elif o in ('-a', '--append'):
        is_append = True

if not output_target:
    raise ValueError('Target file must be specified.')

# do redirection
buffer = bytearray(8192)
stdin = sys.stdin
outcon = sys.stderr if is_stderr else sys.stdout

with open(output_target, ('ab' if is_append else 'wb')) as f:
    # Use the file descriptor instead of file object will prevent
    # the buffering of Python.
    stdin_fd = stdin.fileno()
    file_fd = f.fileno()
    outcon_fd = outcon.fileno()

    try:
        while True:
            buf = os.read(stdin_fd, BUFLEN)
            if not buf:
                break
            os.write(file_fd, buf)
            os.write(outcon_fd, buf)
    except OSError as ex:
        if sys.platform != 'win32':
            # 9 = "Bad file descriptor"
            # 4 = "Interrupted system call"
            if ex.errno not in (4, 9):
                raise
        else:
            raise

# shutdown the process immediately without any further cleanup
os._exit(0)
