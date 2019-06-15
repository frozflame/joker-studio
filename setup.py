#!/usr/bin/env python3
# coding: utf-8

import os
import re

from setuptools import setup, find_packages

# CAUTION:
# Do NOT import your package from your setup.py

namespace = 'joker'
package_name = 'studio'
description = 'CLI tools for media file editing, wrapping FFmpeg and others'


def read(filename):
    with open(filename) as f:
        return f.read()


def version_find():
    if namespace:
        path = '{}/{}/__init__.py'.format(namespace, package_name)
    else:
        path = '{}/__init__.py'.format(package_name)
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
    'name': package_name,
    'version': version_find(),
    'description': '' + description,
    'keywords': '',
    'url': 'https://github.com/frozflame/joker-studio',
    'author': 'anonym',
    'author_email': 'anonym@example.com',
    'license': "GNU General Public License (GPL)",
    'packages': find_packages(exclude=['test_*']),
    'zip_safe': False,
    'install_requires': read("requirements.txt"),
    'entry_points': {'console_scripts': ['dio=joker.studio.main:registry']},
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    # ensure copy static file to runtime directory
    'include_package_data': True,
    'long_description': read('README.md'),
    'long_description_content_type': "text/markdown",
}

if namespace:
    config['name'] = '{}-{}'.format(namespace, package_name)
    config['namespace_packages'] = [namespace]

setup(**config)
