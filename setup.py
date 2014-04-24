#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension
#from distutils.core import Extension, setup
import numpy as np  # Third-party modules - we depend on numpy for everything

# Obtain the numpy include directory.  This logic works across numpy versions.
numpy_include = np.get_include()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
required = open('requirements.txt').read().splitlines()

setup(
    name='wax',
    version='2.1.0',
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
        'wax', 'wax.EventAnalyzer', 'wax.EventBuilder',
        'wax.Database',
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
    ext_modules=[Extension("_wax_compiled_helpers",
                           ["wax/wax_compiled_helpers.i", "wax/wax_compiled_helpers.c"],
                           include_dirs=[numpy_include],
                           extra_compile_args=[],
    )],

)
