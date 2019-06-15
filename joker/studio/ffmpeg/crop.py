#!/usr/bin/env python3
# coding: utf-8
import argparse
import pathlib

from joker.studio.common import utils
from joker.studio.common.info import MediaInfo
from joker.studio.ffmpeg.filters import vf_crop


def mkcod_crop(path, outpath, head, tail, *margins):
    xinfo = MediaInfo(path)
    width = xinfo.video.width
    height = xinfo.video.height
    duration = xinfo.get_video_duration()

    cod = utils.CommandOptionDict([
        ('i', path),
        ('ss', head),
        ('t', duration - head - tail),
        ('c:a', 'copy'),
    ])
    if margins:
        cod['vf'] = vf_crop(width, height, *margins)
    else:
        cod['c:v'] = 'copy'
    return cod('ffmpeg', outpath)


def run(prog=None, args=None):
    desc = 'rename files'
    parser = argparse.ArgumentParser(prog=prog, description=desc)

    parser.add_argument(
        '-c', '--crop', type=float, nargs=4,
        metavar=('top', 'right', 'bottom', 'left'),
        help='crop video in image dimensions')

    parser.add_argument(
        '-t', '--trim', type=float, nargs=2,
        metavar=('head', 'tail'),
        help='trim media in time dimension')

    utils.add_dry_option(parser)
    parser.add_argument('paths', metavar='PATH', nargs='+', help='files')
    ns = parser.parse_args(args)
    head, tail = ns.trim or (0, 0)
    for path in ns.paths:
        px = pathlib.Path(path)
        outpath = px.with_suffix('.crop' + px.suffix)
        cod = mkcod_crop(path, outpath, head, tail, *ns.crop)
        cod.run(ns.dry)


if __name__ == '__main__':
    run()
