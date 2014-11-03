#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension
import distutils.ccompiler # used for library checking

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
required = open('requirements.txt').read().splitlines()

boost_library = ''

compiler=distutils.ccompiler.new_compiler()
lib_dirs=['/usr/lib', '/opt/local/lib/', '/usr/lib/x86_64-linux-gnu/']
if compiler.find_library_file(lib_dirs, 'boost_python-py34'):
    boost_library = 'boost_python-py34'
elif compiler.find_library_file(lib_dirs, 'boost_python3-mt'):
    boost_library = 'boost_python3-mt'
elif compiler.find_library_file(lib_dirs, 'boost_python3'):
    boost_library = 'boost_python3'
elif compiler.find_library_file(lib_dirs, 'boost_python'):
    print("Warning: using non-py3 specific boost")
    boost_library = 'boost_python'
else:
    raise RuntimeError("Cannot find boost")

libs = ['mongoclient', 'snappy'] 
libs += [x for x in [boost_library, 'boost_thread', 'boost_filesystem', 'boost_program_options', 'boost_system', 'ssl', 'crypto', 'pthread'] if compiler.find_library_file(lib_dirs, x)]
print(libs)


setup(
    name='wax',
    version='2.2.1',
    description='Generic particle-physics software trigger and data processor.',
    long_description=readme + '\n\n' + history,
    author='Christopher Tunnell',
    author_email='ctunnell@nikhef.nl',
    url='https://github.com/tunnell/wax',
    download_url='https://github.com/tunnell/wax/tarball/master',
    scripts = [ 'bin/event-builder',
               ],
    packages=[
        'wax', 'wax.EventBuilder', 
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
                           extra_compile_args=['-m64', '-O3',],
                           extra_link_args=[],
                           libraries=libs,
                           library_dirs=lib_dirs,
                           )],

)
