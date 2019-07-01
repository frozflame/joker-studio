#!/usr/bin/env python3
# coding: utf-8

import argparse
import pathlib

from joker.studio.aux import utils
from joker.studio.ffmpeg.filters import vf_subtitle


def mkcod_subtitle(path, subpath, styles, outpath):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('c:a', 'copy'),
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
    utils.add_dry_option(parser)
    parser.add_argument('-s', '--sub', metavar='PATH', help='an SRT file')
    parser.add_argument('path', metavar='PATH', help='a video file')
    ns = parser.parse_args(args)
    px = pathlib.Path(ns.path)
    subpath = ns.sub or px.with_suffix('.srt')
    outpath = px.with_suffix('.wSub' + px.suffix)
    cod = mkcod_subtitle(ns.path, subpath, _styles, outpath)
    cod.run(ns.dry)


if __name__ == '__main__':
    run()
