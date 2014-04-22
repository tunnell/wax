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
    name='wax',
    version='1.9.0',
    description='Generic particle-physics software trigger with flash ADCs.',
    long_description=readme + '\n\n' + history,
    author='Christopher Tunnell',
    author_email='ctunnell@nikhef.nl',
    url='https://github.com/tunnell/wax',
    download_url='https://github.com/tunnell/wax/tarball/master',
    scripts = ['bin/wax-on',
               'bin/wax-off',
               'bin/file-builder',
               'bin/event-builder',
               ],
    packages=[
        'wax', 'wax.core', 'wax.EventBuilder',
        'wax.Database', 'wax.Trigger',
    ],
    package_dir={'wax': 'wax'},
    include_package_data=True,
    install_requires=required,
    license="BSD",
    zip_safe=False,
    keywords='wax',
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
