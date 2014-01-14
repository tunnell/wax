#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from setuptools import setup
import cito

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
required = open('requirements.txt').read().splitlines()

setup(
    name='cito',
    version=cito.__version_string__,
    description='This code consitutes the framework for the XENON software trigger.',
    long_description=readme + '\n\n' + history,
    author='Christopher Tunnell',
    author_email='ctunnell@nikhef.nl',
    url='https://github.com/tunnell/cito',
    download_url='https://github.com/tunnell/cito/tarball/master',
    packages=[
        'cito', 'cito.core', 'cito.EventBuilder', 'cito.FileBuilder', 'cito.Trigger',
    ],
    package_dir={'cito': 'cito'},
    include_package_data=True,
    install_requires=required,
    entry_points={
        'console_scripts': [
            'cito = cito.main:main'
        ],
        'cito.main': [
            'doc inspector = cito.DocInspector:Inspector',
            'db reset = cito.DBOperations:DBReset',
            'db inspector = cito.DBOperations:DBInspector',
            'db repair = cito.DBOperations:DBRepair',
            'db purge = cito.DBOperations:DBPurge',
            'duplicates = cito.DBOperations:DBDuplicates',
            'process = cito.Process:ProcessToMongoCommand',
        ],
    },
    license="BSD",
    zip_safe=False,
    keywords='cito',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',

)
