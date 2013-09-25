#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='cito',
    version='0.1.0',
    description='This code consitutes the framework for the XENON software trigger.',
    long_description=readme + '\n\n' + history,
    author='Christopher Tunnell',
    author_email='ctunnell@nikhef.nl',
    url='https://github.com/tunnell/cito',
    download_url='https://github.com/tunnell/cito/tarball/master',
    packages=[
        'cito', 'cito.helpers',
    ],
    package_dir={'cito': 'cito'},
    include_package_data=True,
    install_requires=['cliff'],
    entry_points={
        'console_scripts': [
            'cito = cito.main:main'
        ],
        'cito.main': [
            'doc inspector = cito.inspector:Inspector',
            'db reset = cito.db_operations:DBReset',
            'db inspector = cito.db_operations:DBCount',
            'process = cito.online_processing:Process'
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
