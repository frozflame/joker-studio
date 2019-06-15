#!/usr/bin/env python3
# coding: utf-8

import argparse
import os
import pathlib

from joker.cast.syntax import printerr

from joker.studio.common import utils


def mkcod_video_poster(path, outpath, pos):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('ss', pos),
        ('vframes', 1),
    ])
    return cod('ffmpeg', outpath)


def mkcod_pipe_thumbnail(path, pos, w, h):
    cod = utils.CommandOptionDict([
        ('i', path),
        ('ss', pos),
        ('vframes', 1),
        ('vcodec', 'png'),
        ('f', 'image2pipe'),
        ('s', '{}x{}'.format(w, h))
    ])
    return cod('ffmpeg', '-')


def mkcod_video_thumbnail(path, outpath, tspan, count=None, size=None):
    fps = 1 / float(tspan)
    cod = utils.CommandOptionDict([
        ('i', path),
        ('vf', 'fps={}'.format(fps)),
    ])
    if count is not None:
        cod['vframes'] = count
    if size is not None:
        cod['s'] = '{}x{}'.format(*size)
    if outpath == '-':
        cod['vcodec'] = 'png'
        cod['f'] = 'image2pipe'
    elif count != 1 and '%' not in outpath:
        pm, ext = os.path.splitext(outpath)
        outpath = pm + '.Thumb_%04d' + ext
    return cod('ffmpeg', outpath)


def make_poster(path, ns):
    bx = os.path.splitext(path)
    outpath = bx[0] + '.' + ns.fmt
    cod = mkcod_video_poster(path, outpath, 1)
    cod.run(ns.dry)


def make_thumbnails(path, ns):
    ext = ('.' + ns.format).replace('..', '.')
    px = pathlib.Path(path)
    outpath = px.with_suffix(ext)
    cod = mkcod_video_thumbnail(path, outpath, ns.tspan)
    cod.run(ns.dry)


def run_poster(prog=None, args=None):
    desc = 'generate poster images from videos'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        '-f', '--format', dest='fmt', choices=['png', 'jpg'],
        default='jpg', help='out image format')

    parser.add_argument(
        '--dry', action='store_true',
        help='print ffmpeg command but do not execute it')

    parser.add_argument(
        'paths', metavar='PATH', nargs='+', help='an audio/video file')
    ns = parser.parse_args(args)
    for p in ns.paths:
        try:
            make_poster(p, ns)
        except Exception as e:
            printerr('path:', p)
            printerr(e)


def run(prog=None, args=None):
    desc = 'generate thumbnail images from a video'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    utils.add_dry_option(parser)

    parser.add_argument(
        '-t', '--tspan', type=int, default=60,
        help='time span between each image, in second')

    parser.add_argument(
        '-f', '--format', default='jpg', help='output image format')

    parser.add_argument(
        '-l', '--label', help='output file label')

    parser.add_argument(
        'paths', metavar='PATH', nargs='+', help='an audio file')

    ns = parser.parse_args(args)
    for p in ns.paths:
        make_poster(p, ns)

