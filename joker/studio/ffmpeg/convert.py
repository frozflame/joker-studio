#!/usr/bin/env python3
# coding: utf-8

import argparse
import os
import sys

from joker.cast.syntax import printerr

from joker.studio.common import utils


def mkcod_image_convert(path, outpath):
    cmd = 'convert'
    if sys.platform.startswith('win'):
        cmd = 'imagemagick'
    cod = utils.CommandOptionDict()
    return cod(cmd, path, outpath)


def mkcod_convert_ts_mp4(path, outpath):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('c:v', 'libx264'),
        ('c:a', 'copy'),
        ('bsf:a', 'aac_adtstoasc'),
    ])
    return cod('ffmpeg', outpath)


def mkcod_convert_gif_mp4(path, outpath):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('movflags', 'faststart'),
        ('pix_fmt', 'yuv420p'),
        ('vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2'),
    ])
    return cod('ffmpeg', outpath)


def mkcod_convert_to_mp3(path, outpath):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('c:a', 'libmp3lame'),
    ])
    return cod('ffmpeg', outpath)


_all_formats = ['mp3', 'mp4', 'jpg', 'png', 'bmp', 'webp']
_image_formats = {'jpg', 'png', 'bmp'}


def convert_a_file(path, ns):
    base_path, ext = os.path.splitext(path)
    outpath = base_path + '.' + ns.fmt
    fmt = ext[1:].lower()
    if fmt == 'ts' and ns.fmt == 'mp4':
        cod = mkcod_convert_ts_mp4(path, outpath)
    elif fmt == 'gif' and ns.fmt == 'mp4':
        cod = mkcod_convert_gif_mp4(path, outpath)
    elif ns.fmt == 'mp3':
        cod = mkcod_convert_to_mp3(path, outpath)
    elif fmt in _image_formats and ns.fmt in _image_formats:
        cod = mkcod_image_convert(path, outpath)
    else:
        raise ValueError('conversion not supported')
    cod.run(ns.dry)


def run(prog=None, args=None):
    desc = 'convert audio/video format'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    utils.add_dry_option(parser)

    parser.add_argument(
        '-f', '--format', dest='fmt', choices=_all_formats,
        default='mp4', help='out audio/video format')

    parser.add_argument(
        '--dry', action='store_true',
        help='print ffmpeg command but do not execute it')

    parser.add_argument(
        'paths', metavar='PATH', nargs='+', help='an audio/video file')

    ns = parser.parse_args(args)
    for p in ns.paths:
        try:
            convert_a_file(p, ns)
        except Exception as e:
            printerr('path:', p)
            printerr(e)


if __name__ == '__main__':
    run()
