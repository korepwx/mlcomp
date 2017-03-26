# -*- coding: utf-8 -*-
import codecs
import os
import subprocess
import sys
import unittest

import six

from mlcomp.utils import TemporaryDirectory


class UtilsTestCase(unittest.TestCase):

    def test_duplicate_console_output(self):
        with TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'console.log')
            proc_out = subprocess.check_output([
                sys.executable,
                os.path.abspath(os.path.join(
                    os.path.dirname(__file__),
                    '_duplicate_console_output_check.py'
                )),
                log_file
            ])
            if isinstance(proc_out, six.binary_type):
                proc_out = proc_out.decode('utf-8')
            with codecs.open(log_file, 'rb', 'utf-8') as f:
                file_out = f.read()
            answer = ('from print\nfrom stdout.write\nfrom stderr.write\n'
                      'os.system+stdout\nos.system+stderr\n')
            self.assertEqual(proc_out.replace('\r\n', '\n'), answer)
            self.assertEqual(file_out.replace('\r\n', '\n'), answer)
