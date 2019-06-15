#!/usr/bin/env python3
# coding: utf-8

import argparse

from joker.studio.common.info import MediaInfo
from joker.studio.common.utils import CommandOptionDict
from joker.studio.ffmpeg.filters import af_fade


# TODO: vf_fade


def mkcod_whole_audio_fade(path, fadein, fadeout, outpath):
    xinfo = MediaInfo(path)
    duration = xinfo.get_audio_duration()
    afade = af_fade(0, duration, fadein, fadeout)
    cod = CommandOptionDict([
        ('i', path),
        ('af', afade),
    ])
    return cod('ffmpeg', outpath)


def _convert_a_file(path, ns):
    import os
    ext = '.{}.{}'.format(ns.label or '', ns.fmt)
    ext = ext.replace('..', '.')
    ext = ext.replace('..', '.')
    outpath = os.path.splitext(path)[0] + ext
    cod = mkcod_whole_audio_fade(path, ns.a, ns.b, outpath)
    cod.run(ns.dry)


def run(prog=None, args=None):
    desc = 'add fade-in and fade-out to audios'
    parser = argparse.ArgumentParser(prog=prog, description=desc)

    parser.add_argument(
        '-a', type=int, default=4, help='fade in length in second')

    parser.add_argument(
        '-b', type=int, default=5, help='fade out length in second')

    parser.add_argument(
        '-f', '--format', dest='fmt',
        default='wav', help='out audio format')

    parser.add_argument(
        '-l', '--label', help='out file label')

    parser.add_argument(
        '--dry', action='store_true',
        help='print ffmpeg command but do not execute it')

    parser.add_argument(
        'paths', metavar='PATH', nargs='+', help='an audio file')
    ns = parser.parse_args(args)

    if ns.label is None:
        ns.label = 'F{}F{}'.format(ns.a, ns.b)
    for p in ns.paths:
        _convert_a_file(p, ns)


if __name__ == '__main__':
    run()
