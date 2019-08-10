#!/usr/bin/env python3
# coding: utf-8

import argparse
import datetime
import hashlib
import itertools
import os
import pathlib
import re
from functools import partial
from subprocess import PIPE

from joker.studio.aux import utils
from joker.studio.aux.info import MediaInfo
from joker.studio.aux.utils import format_help_section
from joker.studio.ffmpeg.thumb import mkcod_video_thumbnail


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
    # imagehash is slow to import, 250ms
    import imagehash
    from PIL import Image
    try:
        ih = imagehash.average_hash(Image.open(str(px)))
    except OSError:
        return 'NotImage'
    return str(ih).upper()


def compute_video_hash(px, hash_size=4, img_count=4):
    import imagehash
    path = str(px)
    xinfo = MediaInfo(path)
    duration = xinfo.get_video_duration()
    params = {
        'tspan': 1. * duration / (img_count + 1),
        'count': img_count,
        'size': (160, 90),
    }
    cod = mkcod_video_thumbnail(path, '-', **params)
    with open(os.devnull, 'w') as devnull:
        cp = cod.run(quiet=True, stdout=PIPE, stderr=devnull)
    images = utils.split_stream_png(cp.stdout)
    ihs = [imagehash.average_hash(img, hash_size) for img in images]
    return ''.join([str(ih) for ih in ihs]).upper()


def get_duration(px):
    parts = ['Dur']
    dur = int(MediaInfo(px).get_duration())
    dt = datetime.datetime.fromtimestamp(dur)
    if dt.hour:
        parts.append(str(dt.hour).rjust(2, '0') + 'h')
    if dt.hour or dt.minute:
        parts.append(str(dt.minute).rjust(2, '0') + 'm')
    parts.append(str(dt.second).rjust(2, '0') + 's')
    return ''.join(parts)


def sanitize(px):
    # windows file names disallow:  <>:"/|?* back-slash
    # need to be quoted on unix:    !$&();=@[^`
    # x27 single-quote
    # x5C back-slash
    # x7F delete
    regex = re.compile(r'(^-|[\x00-\x20!$&();=@[^`<>:"/|?*\x27\x5C\x7F]+)')
    name = regex.sub('%', px.name)
    stem, ext = os.path.splitext(name)
    return stem + _extcorrection.get(ext.lower(), ext)


def camel_case(px):
    parts = px.name.split()
    parts = [w[0].upper() + w[1:] for w in parts]
    return ''.join(parts)


_known_fields = {
    'IH': compute_image_hash,
    'VH': compute_video_hash,
    'MD5': partial(compute_hash, algo='md5'),
    'SHA1': partial(compute_hash, algo='sha1'),
    'SHA256': partial(compute_hash, algo='sha256'),
    'SHA512': partial(compute_hash, algo='sha512'),
    'WxH': lambda px: '{}x{}'.format(*MediaInfo(str(px)).get_size()),
    'DURATION': lambda px: get_duration,
    'STEM': lambda px: px.stem,
    'EXT': lambda px: px.suffix[1:],
    'NAME': lambda px: px.name,
    'CCNAME': camel_case,
    'SANNAME': sanitize,
}

_variables = {
    'IH': 'imagehash.average_hash()',
    'VH': 'video hash based on imagehash.average_hash()',
    'MD5': '32 hex digits',
    'SHA1': '40 hex digits',
    'SHA256': '64 hex digits',
    'SHA512': '128 hex digits',
    'WxH': 'image or video size',
    'DURATION': 'audio or video duration',
    'EXT': 'original extension, without a leading dot',
    'STEM': 'original file name without extension',
    'NAME': 'original file name',
    'CCNAME': 'CamelCased file name',
    'SANNAME': 'sanitized file name',
}

_safe_presets = {
    'default': 'md5-MD5.NAME',
    'md5': 'md5-MD5.NAME',
    'sha1': 'sha1-SHA1.NAME',
    'ih': 'ih-IH.NAME',
    'vh': 'vh-VH.NAME',
    's': 'ser-SERIAL.NAME',
    'avatar': 'avatar-WxH.NAME',
    'i': 'img-WxH.NAME',
    'a': 'a-DURATION.NAME',
    'v': 'v-WxH-DURATION.NAME',
    'n': 'NAME',
}

_risky_presets = {
    'md5%': 'md5-MD5.EXT',
    'sha1%': 'sha1-SHA1.EXT',
    'ih%': 'ih-IH.EXT',
    'vh%': 'vh-VH.EXT',
    's%': 'ser-SERIAL.EXT',
    'cc': 'CCNAME',
    'san': 'SANNAME',
}

# language=regex
_extcorrection = {
    '.jpeg': '.jpg',
    '.mpeg': '.mpg',
    '.tiff': '.tif',
    '.png_large': '.png',
    '.jpg_large': '.jpg',
    '.bmp_large': '.bmp',
}


def presets_lookup(name):
    return _safe_presets.get(name) or _risky_presets.get(name, name)


class FormulaRenamer(object):
    def __init__(self, formula, clear=False, start=101):
        self._clear = clear
        self._serial = itertools.count(start)
        formula = presets_lookup(formula)
        self._fields = re.split(r'(\W+)', formula)

    @staticmethod
    def clear_preset_prefixes(px):
        _patterns = [
            re.compile(r'^(md5|sha1)-[0-9a-f]{32,40}\.'),
            re.compile(r'^(img|avatar|v|a)(-\d+x\d+|-Dur[0-9hms]+){1,2}\.'),
            re.compile(r'^(ih|vh)-[0-9A-F]{10,20}.'),
        ]
        name = px.name
        for pat in _patterns:
            name = re.sub(pat, '', name)
        return px.with_name(name)

    def make_name(self, px):
        parts = []
        if self._clear:
            px = self.clear_preset_prefixes(px)
        for k in self._fields:
            if k in _known_fields:
                s = _known_fields[k](px)
                parts.append(s)
            elif k == 'SERIAL':
                parts.append(str(next(self._serial)))
            else:
                parts.append(k)
        return ''.join(parts)

    def rename(self, path):
        px = pathlib.Path(path)
        name = self.make_name(px)
        px.rename(px.with_name(name))


def run(prog=None, args=None):
    desc = 'Rename files with a formula'
    s = ' (case sensitive)'
    epilog = '\n'.join([
        format_help_section('Variables' + s, _variables),
        format_help_section('Safe presets', _safe_presets),
        format_help_section('Risky presets', _risky_presets),
    ])

    pr = argparse.ArgumentParser(
        prog=prog, description=desc, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    pr.add_argument('-f', '--formula', default=_safe_presets['default'],
                    help='a name formula, or one of the presets')

    pr.add_argument('-c', '--clear', action='store_true',
                    help='clear previously add tags using presets')

    pr.add_argument('-i', '--start', default=101, type=int,
                    help='start number of the SERIAL variable')

    pr.add_argument('files', metavar='PATH', nargs='+')

    ns = pr.parse_args(args)
    fren = FormulaRenamer(ns.formula, ns.clear, ns.start)
    for path in ns.files:
        fren.rename(path)
