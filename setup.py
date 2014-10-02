#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
required = open('requirements.txt').read().splitlines()

setup(
    name='wax',
    version='2.2.1',
    description='Generic particle-physics software trigger and data processor.',
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
        'wax', 'wax.EventBuilder', 'wax.EventAnalyzer',
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
    ext_modules=[Extension("ebcore",
                           ["wax/EventBuilder/ebcore.cpp"],
                           extra_compile_args=['-m64', '-g', '-Wl,--export-dynamic'],
                           extra_link_args=['-Wl,--export-dynamic'],
                           libraries=['boost_python-py34', 'mongoclient', 'boost_thread', 'boost_filesystem', 'boost_program_options', 'boost_system', 'ssl', 'crypto', 'pthread'],
                           )],

)
