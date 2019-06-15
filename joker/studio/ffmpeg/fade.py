#!/usr/bin/env python3
# coding: utf-8

import argparse
import pathlib

from joker.studio.common import utils
from joker.studio.common.info import MediaInfo
from joker.studio.common.utils import CommandOptionDict
from joker.studio.ffmpeg.filters import af_fade, vf_fade


def mkcod_fade(path, outpath, vfadein=0, vfadeout=0, afadein=0, afadeout=0):
    xinfo = MediaInfo(path)
    duration = xinfo.get_audio_duration()
    cod = CommandOptionDict([
        ('i', path),
    ])

    if vfadein or vfadeout:
        cod['vf'] = vf_fade(0, duration, vfadein, vfadeout)
    else:
        cod['c:v'] = 'copy'

    if afadein or afadeout:
        cod['af'] = af_fade(0, duration, afadein, afadeout)
    else:
        cod['c:a'] = 'copy'

    return cod('ffmpeg', outpath)


def run(prog=None, args=None):
    desc = 'add fade-in and fade-out to audios'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    utils.add_dry_option(parser)

    parser.add_argument(
        '-a', type=int, nargs=2, metavar=('IN', 'OUT'),
        help='audio fade-in and fade-out lengths, in sec')

    parser.add_argument(
        '-v', type=int, nargs=2, metavar=('IN', 'OUT'),
        help='video fade-in and fade-out lengths, in sec')

    parser.add_argument(
        'paths', metavar='PATH', nargs='+', help='input video files')

    ns = parser.parse_args(args)
    for path in ns.paths:
        px = pathlib.Path(path)
        outpath = px.with_suffix('.fade' + px.suffix)
        vfi, vfo = ns.v or (0, 0)
        afi, afo = ns.a or (0, 0)
        cod = mkcod_fade(path, outpath, vfi, vfo, afi, afo)
        cod.run(ns.dry)


if __name__ == '__main__':
    run()
