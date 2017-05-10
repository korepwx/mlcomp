# -*- coding: utf-8 -*-
import codecs
import os
import re

FILE_NAME_PATTERN = re.compile(r'.*\.py$')
LINE_PROCESS_PATTERN = re.compile(r'(.*?)[ ]+\r?\n$', re.MULTILINE)


def process_dir(path, relpath):
    for fname in os.listdir(path):
        if fname == 'node_modules':
            continue
        f_path = os.path.join(path, fname)
        f_relpath = relpath + '/' + fname if relpath else fname
        if os.path.isdir(f_path):
            process_dir(f_path, f_relpath)
        elif FILE_NAME_PATTERN.match(f_relpath):
            with codecs.open(f_path, 'rb', 'utf-8') as fin:
                lines = list(fin)
            modify_count = 0
            for i, line in enumerate(lines):
                m = LINE_PROCESS_PATTERN.match(line)
                if m:
                    lines[i] = m.group(1) + '\n'
                    modify_count += 1
            if modify_count > 0:
                cnt = ''.join(lines)
                with codecs.open(f_path, 'wb', 'utf-8') as fout:
                    fout.write(cnt)
                print('%s: %d line(s)' % (f_relpath, modify_count))


for fname in ('scripts', 'tests', 'mlcomp'):
    process_dir(
        os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', fname)),
        fname
    )
