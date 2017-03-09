import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from madoka.utils import duplicate_console_output

with duplicate_console_output(sys.argv[1]):
    print('from print')
    sys.stdout.flush()
    sys.stdout.write('from stdout.write\n')
    sys.stdout.flush()
    sys.stderr.write('from stderr.write\n')
    sys.stderr.flush()
    os.system('echo os.system+stdout')
    subprocess.check_call([
        sys.executable,
        '-c',
        'import sys; sys.stderr.write("os.system+stderr\\n");'
        'sys.stderr.flush()'
    ])
