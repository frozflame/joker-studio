#!/usr/bin/env python3
# coding: utf-8

import argparse
import os

from joker.studio.common.utils import CommandOptionDict
from joker.studio.ffmpeg.filters import vf_subtitle


def mkcod_subtitle(path, subpath, styles, outpath):
    cod = CommandOptionDict([
        ('i', path),
        ('vf', vf_subtitle(subpath, styles)),
    ])
    return cod('ffmpeg', outpath)


_ref_styles = {
    'Alignment': None,
    'Angle': None,
    'BackColour': None,
    'Bold': None,
    'BorderStyle': None,
    'Encoding': None,
    'Fontname': None,
    'Fontsize': None,
    'Italic': None,
    'MarginL': None,
    'MarginR': None,
    'MarginV': None,
    'Name': None,
    'Outline': None,
    'OutlineColour': None,
    'PrimaryColour': None,
    'ScaleX': None,
    'ScaleY': None,
    'SecondaryColour': None,
    'Shadow': None,
    'Strikeout': None,
    'Underline': None,
}

_styles = [
    ('Fontname', 'Khmer MN'),
    ('Fontsize', 46),
    ('BackColour', '&HA0000000'),
    ('BorderStyle', 4),
    # ('PrimaryColour', '&HADAEC4'),
    ('OutlineColour', '&H800000')
]


def run(prog=None, args=None):
    desc = 'burn subtitle into a video'
    parser = argparse.ArgumentParser(prog=prog, description=desc)

    parser.add_argument(
        '--dry', action='store_true',
        help='print ffmpeg command but do not execute it')

    parser.add_argument('path', metavar='PATH', help='a video file')

    parser.add_argument(
        '-e', '--ext', default='mp4', help='output file extension')

    parser.add_argument(
        '-s', '--sub', metavar='PATH', help='an SRT file')
    ns = parser.parse_args(args)

    pstem, ext = os.path.splitext(ns.path)
    if ns.sub is None:
        ns.sub = pstem + '.srt'
    outpath = pstem + '.wSub.' + ns.ext.replace('.', '')
    cod = mkcod_subtitle(ns.path, ns.sub, _styles, outpath)
    cod.run(ns.dry)


if __name__ == '__main__':
    run()
