#!/usr/bin/env python3
# coding: utf-8

import os
import re

from setuptools import setup, find_namespace_packages

# CAUTION:
# Do NOT import your package from your setup.py

nsp_name = 'joker'
pkg_name = 'studio'
project_name = 'joker-studio'
description = 'CLI tools for media file editing, wrapping FFmpeg and others'


def read(filename):
    with open(filename) as f:
        return f.read()


def version_find():
    if nsp_name:
        path = '{}/{}/__init__.py'.format(nsp_name, pkg_name)
    else:
        path = '{}/__init__.py'.format(pkg_name)
    root = os.path.dirname(__file__)
    path = os.path.join(root, path)
    regex = re.compile(
        r'''^__version__\s*=\s*('|"|'{3}|"{3})([.\w]+)\1\s*(#|$)''')
    with open(path) as fin:
        for line in fin:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            mat = regex.match(line)
            if mat:
                return mat.groups()[1]
    raise ValueError('__version__ definition not found')


config = {
    'name': project_name,
    'version': version_find(),
    'description': description,
    'keywords': '',
    'url': 'https://github.com/frozflame/joker-studio',
    'author': 'anonym',
    'author_email': 'anonym@example.com',
    'license': "GNU General Public License (GPL)",
    'packages': find_namespace_packages(include=['joker.*']),
    'zip_safe': False,
    'install_requires': read("requirements.txt"),
    'entry_points': {
        'console_scripts': ['dio = joker.studio.__main__:registry']
    },
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    # ensure copy static file to runtime directory
    'include_package_data': True,
    'long_description': read('README.md'),
    'long_description_content_type': "text/markdown",
}

if nsp_name:
    config['name'] = project_name,
    config['namespace_packages'] = [nsp_name]

setup(**config)
