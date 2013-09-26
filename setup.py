#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import os

try:
    import numpy
    from Cython.Distutils import build_ext
except ImportError:
    print("You must install numpy and Cython first (e.g., easy_install numpy Cython)")
    raise

from setuptools import setup

from distutils.extension import Extension

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
required = open('requirements.txt').read().splitlines()


module1 = Extension("cito.helpers.cInterfaceV1724", ["cito/helpers/cInterfaceV1724.pyx"],
                    extra_compile_args=['-O3'])

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
    install_requires=required,
    entry_points={
        'console_scripts': [
            'cito = cito.main:main'
        ],
        'cito.main': [
            'doc inspector = cito.inspector:Inspector',
            'db reset = cito.db_operations:DBReset',
            'db inspector = cito.db_operations:DBCount',
            'db repair = cito.db_operations:DBRepair',
            'db purge = cito.db_operations:DBPurge',
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
    cmdclass={'build_ext': build_ext},
    include_dirs=[numpy.get_include()],
    ext_modules = [module1],
)
