#!/usr/bin/env python3
# coding: utf-8

import argparse
import datetime
import hashlib
import itertools
import pathlib
import re
from functools import partial

from joker.studio.aux.info import MediaInfo
from joker.studio.aux.utils import format_help_section


def compute_hash(px, algo='md5'):
    chunksize = 1024
    hashfunc = hashlib.new(algo)
    with open(px, 'rb') as fin:
        chunk = fin.read(chunksize)
        while chunk:
            hashfunc.update(chunk)
            chunk = fin.read(chunksize)
    return hashfunc.hexdigest()


def compute_image_hash(px):
    import imagehash
    from PIL import Image
    try:
        ih = imagehash.average_hash(Image.open(str(px)))
    except OSError:
        return 'NotImage'
    return str(ih).upper()


def get_duration(px):
    parts = ['Dur']
    dur = int(MediaInfo(str(px)).get_duration())
    dt = datetime.datetime.fromtimestamp(dur)
    if dt.hour:
        parts.append(str(dt.hour).rjust(2, '0') + 'h')
    if dt.hour or dt.minute:
        parts.append(str(dt.minute).rjust(2, '0') + 'm')
    parts.append(str(dt.second).rjust(2, '0') + 's')
    return ''.join(parts)


_known_fields = {
    'IH': compute_image_hash,
    'MD5': partial(compute_hash, algo='md5'),
    'SHA1': partial(compute_hash, algo='sha1'),
    'SHA256': partial(compute_hash, algo='sha256'),
    'SHA512': partial(compute_hash, algo='sha512'),
    'EXT': lambda px: px.suffix[1:],
    'STEM': lambda px: px.stem,
    'NAME': lambda px: px.name,
    'WxH': lambda px: '{}x{}'.format(*MediaInfo(str(px)).get_size()),
    'DURATION': lambda px: get_duration,
    'SERIAL': lambda px: '{:03}'.format(next(_serial)),
}

_variables = {
    'IH': 'imagehash.average_hash()',
    'MD5': '32 hex digits',
    'SHA1': '40 hex digits',
    'SHA256': '64 hex digits',
    'SHA512': '128 hex digits',
    'EXT': 'original extension, without a leading dot',
    'STEM': 'original file name without extension',
    'NAME': 'original file name',
    'WxH': 'image or video size',
    'DURATION': 'audio or video duration',
}

_presets = {
    '(default)': 'md5-MD5.NAME',
    'md5': 'md5-MD5.NAME',
    'sha1': 'sha1-SHA1.NAME',
    'avatar': 'avatar-WxH.NAME',
    'i': 'img-WxH.NAME',
    'a': 'a-DURATION.NAME',
    'v': 'v-WxH-DURATION.NAME',
    'ih': 'ih-IH.NAME',
    's': 's-SERIAL.NAME',
    '0': 'NAME',
}

# language: regexp
_clean_patterns = [
    r'^md5-\b',
    r'^md5-[0-9a-f]{32}\.',
    r'^sha1-[0-9a-f]{40}\.',
    r'^(img|avatar|v|a)(-\d+x\d+|-Dur[0-9hms]+){1,2}\.',
    r'^ih-[0-9A-F]{10,20}.',
    r'^s-\d+\.',
]

_extcorrection = {
    '.jpeg': '.jpg',
    '.mpeg': '.mpg',
    '.tiff': '.tif',
    '.png_large': '.png',
    '.jpg_large': '.jpg',
    '.bmp_large': '.bmp',
}


class FormulaRenamer(object):
    def __init__(self, formula, clean=False, start=101):
        self.clean = clean
        self.serial = itertools.count(start)
        formula = _presets.get(formula, formula)
        self.fields = re.split(r'(\W+)', formula)

    @staticmethod
    def _clean_name(path):
        px = pathlib.Path(path)
        stem = px.stem
        for pat in _clean_patterns:
            stem = re.sub(pat, '', stem)
        stem = re.sub(r'[.\s]+', '.', stem)
        stem = re.sub(r'\.$', '', stem)
        stem = re.sub(r'^-', '', stem)
        ext = px.suffix.lower()
        ext = _extcorrection.get(ext, ext)
        return px.with_name(stem + ext)

    def make_name(self, px):
        parts = []
        if self.clean:
            px = self._clean_name(px)
        for k in self.fields:
            if k in _known_fields:
                s = _known_fields[k](px)
                parts.append(s)
            elif k == 'SERIAL':
                parts.append(str(next(self.serial)))
            else:
                parts.append(k)
        return ''.join(parts)

    def rename(self, path):
        px = pathlib.Path(path)
        name = self.make_name(px)
        px.rename(px.with_name(name))


def run(prog=None, args=None):
    desc = 'rename files with a formula'
    s = ' (case sensitive)'
    epilog = '\n'.join([
        format_help_section('variables' + s, _variables),
        format_help_section('presets', _presets),
    ])

    parser = argparse.ArgumentParser(
        prog=prog, description=desc, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-f', '--formula', default=_presets['(default)'],
                        help='a name formula, or one of the presets')

    parser.add_argument('-c', '--clean', action='store_true',
                        help='remove preset-prefixes, ^-, .$, spaces, etc.')

    parser.add_argument('-s', '--start', default=101, type=int,
                        help='start number of the SERIAL variable')

    parser.add_argument('files', metavar='PATH', nargs='+')

    ns = parser.parse_args(args)
    fren = FormulaRenamer(ns.formula, ns.clean, ns.start)
    for path in ns.files:
        fren.rename(path)
