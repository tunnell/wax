#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from setuptools import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
required = open('requirements.txt').read().splitlines()

setup(
    name='cito',
    version='1.9.0',
    description='Generic particle-physics software trigger with flash ADCs.',
    long_description=readme + '\n\n' + history,
    author='Christopher Tunnell',
    author_email='ctunnell@nikhef.nl',
    url='https://github.com/tunnell/cito',
    download_url='https://github.com/tunnell/cito/tarball/master',
    packages=[
        'cito', 'cito.core', 'cito.EventBuilder',
        'cito.Database', 'cito.Trigger',
    ],
    package_dir={'cito': 'cito'},
    include_package_data=True,
    install_requires=required,
    entry_points={
        'console_scripts': [
            'cito = cito.core.main:main'
        ],
        'cito.core.main': [
            'delete = cito.DBOperations:DBDelete',
            'repair = cito.DBOperations:DBRepair',
            'process = cito.EventBuilder.Processor:ProcessCommand',
            'file builder = cito.FileBuilder:FileBuilderCommand',
        ],
    },
    license="BSD",
    zip_safe=False,
    keywords='cito',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',

)
