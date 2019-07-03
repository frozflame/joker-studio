#!/usr/bin/env python3
# coding: utf-8

import argparse
import fnmatch
import os
import sys


def remove_empty_dirs(rootdir, dry=False):
    for directory, dirnames, filenames in os.walk(rootdir):
        if not dirnames and not filenames:
            if not dry:
                os.rmdir(directory)
                print('REMOVED:', directory, file=sys.stderr)
            else:
                print('NOT REMOVED:', directory, file=sys.stderr)


def _check(dir_, name, patterns, empty):
    path = os.path.join(dir_, name)
    if empty and os.path.getsize(path) == 0:
        return path
    for patt in patterns:
        if fnmatch.fnmatch(name, patt):
            return path


def remove_files(rootdir, patterns, empty=False, dry=False):
    _size = os.path.getsize
    _join = os.path.join
    for dir_, dirnames, filenames in os.walk(rootdir):
        for name in filenames:
            path = _check(dir_, name, patterns, empty)
            if not path:
                continue
            if not dry:
                os.remove(path)
                print('REMOVED:', path, file=sys.stderr)
            else:
                print('NOT REMOVED:', path, file=sys.stderr)


_all_presets = {
    'pyc': ['*.pyc'],
    'log': ["*.log"],
    'win': ['desktop.ini', 'thumbs.db'],
    'mac': ['.DS_Store'],
    'mauve': ['mauve*'],
    'blast': [
        '*.phr', '*.pin', '*.psq',
        '*.nhr', '*.nin', '*.nsq',
        "*.nsd", "*.nsi", 'formatdb.log',
    ],
}


def _format_presets_list():
    parts = ['available presets:']
    width = max(len(name) for name in _all_presets)
    for name, patterns in _all_presets.items():
        s1 = (name + ':').ljust(width + 3)
        s2 = ', '.join(patterns)
        parts.append(s1 + s2)
    return '\n  '.join(parts)


def run(prog=None, args=None):
    desc = 'remove (semi-)empty directories'
    pr = argparse.ArgumentParser(
        prog=prog, description=desc,
        epilog=_format_presets_list(),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    pr.add_argument('-d', '--dry', action='store_true',
                    help='just show files to be removed')

    pr.add_argument('-a', '--all-presets',
                    action='store_true', help='use all presets')

    pr.add_argument('-e', '--empty', action='store_true',
                    help='remove all 0 byte files, regardless filename')

    pr.add_argument('target', metavar='dir', help='target directory')

    pr.add_argument('patterns', nargs='*', metavar='pattern',
                    help='preset names or filename patterns')

    ns = pr.parse_args(args)
    name_patterns = []
    if ns.all_presets:
        name_patterns = sum(_all_presets.values(), name_patterns)

    for pat in ns.patterns:
        name_patterns.extend(_all_presets.get(pat, [pat]))
    if name_patterns or ns.empty:
        remove_files(ns.target, set(name_patterns), ns.empty, ns.dry)
    remove_empty_dirs(ns.target, ns.dry)
