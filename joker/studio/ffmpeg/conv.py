#!/usr/bin/env python3
# coding: utf-8

import argparse
import pathlib
import sys

from joker.cast.syntax import printerr

from joker.studio.common import utils


def mkcod_convert(path, outpath):
    cod = utils.CommandOptionDict([('i', path)])
    return cod('ffmpeg', outpath)


def mkcod_image_convert(path, outpath):
    cmd = 'convert'
    if sys.platform.startswith('win'):
        cmd = 'imagemagick'
    cod = utils.CommandOptionDict()
    return cod(cmd, path, outpath)


def _mkcod_convert_ts_mp4(path, outpath):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('c:v', 'libx264'),
        ('c:a', 'copy'),
        ('bsf:a', 'aac_adtstoasc'),
    ])
    return cod('ffmpeg', outpath)


def _mkcod_convert_gif_mp4(path, outpath):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('movflags', 'faststart'),
        ('pix_fmt', 'yuv420p'),
        ('vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2'),
        ('c:v', 'libx264'),
        ('an', []),
    ])
    return cod('ffmpeg', outpath)


def mkcod_convert_to_mp4(path, outpath):
    if path.endswith('.ts'):
        return _mkcod_convert_ts_mp4(path, outpath)
    if path.endswith('.gif'):
        return _mkcod_convert_gif_mp4(path, outpath)
    cod = utils.CommandOptionDict([('i', path)])
    return cod('ffmpeg', outpath)


def mkcod_convert_to_audio(path, outpath):
    cod = utils.CommandOptionDict([('i', path)])
    if outpath.endswith('.mp3'):
        cod['c:a'] = 'libmp3lame'
    return cod('ffmpeg', outpath)


CAT_AUDIO = 1
CAT_VIDEO = 2
CAT_IMAGE = 3


known_extensions = {
    '.mp3': CAT_AUDIO,
    '.wav': CAT_AUDIO,
    '.aac': CAT_AUDIO,
    '.ogg': CAT_AUDIO,
    '.wma': CAT_AUDIO,
    '.jpg': CAT_IMAGE,
    '.bmp': CAT_IMAGE,
    '.png': CAT_IMAGE,
    '.gif': CAT_IMAGE,
    '.mp4': CAT_VIDEO,
    '.mkv': CAT_VIDEO,
    '.flv': CAT_VIDEO,
    '.wmv': CAT_VIDEO,
    '.mov': CAT_VIDEO,
    '.ts': CAT_VIDEO,
    '.flac': CAT_AUDIO,
    '.rmvb': CAT_VIDEO,
}


class UnsupportedConversion(ValueError):
    pass


def check_conversion(inext, outext):
    incat = known_extensions.get(inext)
    outcat = known_extensions.get(outext)
    if incat and outcat and incat == outcat:
        return incat, outcat
    if incat == CAT_VIDEO and outcat == CAT_AUDIO:
        return incat, outcat
    msg = '{} => {}'.format(inext, outext)
    raise UnsupportedConversion(msg)


def convert_a_file(path, ns):
    px = pathlib.Path(path)
    outext = ('.' + ns.fmt).replace('..', '.')

    # cat for category
    incat, outcat = check_conversion(px.suffix, outext)
    outpath = str(px.with_suffix('.conv' + outext))

    if outext == '.mp4':
        cod = mkcod_convert_to_mp4(path, outpath)
    elif outcat == CAT_AUDIO:
        cod = mkcod_convert_to_audio(path, outpath)
    elif incat == CAT_IMAGE and outcat == CAT_IMAGE:
        cod = mkcod_image_convert(path, outpath)
    else:
        cod = mkcod_convert(path, outpath)
    cod.run(ns.dry)


def run(prog=None, args=None):
    desc = 'convert audio/video format'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    utils.add_dry_option(parser)

    parser.add_argument(
        '-f', '--format', dest='fmt',
        default='mp4', help='out audio/video format, e.g. mp4, ogg, ...')

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
