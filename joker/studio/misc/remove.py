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


def remove_files(rootdir, patterns, dry=False):
    for directory, dirnames, filenames in os.walk(rootdir):
        for name in filenames:
            for patt in patterns:
                if fnmatch.fnmatch(name, patt):
                    path = os.path.join(directory, name)
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
    parser = argparse.ArgumentParser(
        prog=prog, description=desc,
        epilog=_format_presets_list(),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        '-d', '--dry', action='store_true',
        help='just show files to be removed')
    parser.add_argument('-a', '--all-presets',
                        action='store_true', help='use all presets')
    parser.add_argument('target', metavar='dir', nargs='?', default='.',
                        help='target directory')
    parser.add_argument('patterns', nargs='*', metavar='pattern',
                        help='preset names or filename patterns')

    ns = parser.parse_args(args)
    name_patterns = []
    if ns.all_presets:
        name_patterns = sum(_all_presets.values(), name_patterns)

    for pat in ns.patterns:
        name_patterns.extend(_all_presets.get(pat, [pat]))
    if name_patterns:
        remove_files(ns.target, set(name_patterns), ns.dry)
    remove_empty_dirs(ns.target, ns.dry)
