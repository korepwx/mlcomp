"""
ML Companion
------------

ML Companion is a set of utilities for data preparation and result analysis
in daily machine learning experiments.
"""
import codecs
import os
import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')
_source_dir = os.path.split(os.path.abspath(__file__))[0]

with open(os.path.join(_source_dir, 'mlcomp/__init__.py'), 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with codecs.open(os.path.join(_source_dir, 'requirements.txt'),
                 'rb', 'utf-8') as f:
    install_requires = list(filter(
        lambda v: v and not v.startswith('#'),
        (s.strip() for s in f.read().split('\n'))
    ))


setup(
    name='MLComp',
    version=version,
    url='https://github.com/korepwx/mlcomp/',
    license='MIT',
    author='Haowen Xu',
    author_email='public@korepwx.com',
    description='A set of utilities for daily machine learning experiments.',
    long_description=__doc__,
    packages=find_packages('.', exclude=['tests', 'tests.*']),
    package_data={
        'mlcomp.board': [
            'templates/*',
            'templates/skeleton/*',
            'static/prod/*',
        ],
        'mlcomp.report': ['demo/mandelbrot.png', 'demo/mandelbrot.pyx'],
    },
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    setup_requires=['setuptools'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points='''
        [console_scripts]
        mlcomp-board=mlcomp.board.cli:main
    '''
)
