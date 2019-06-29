#!/usr/bin/env python3
# coding: utf-8

import pathlib
import sys

from PIL import Image


class AvatarMaker(object):
    def __init__(self, size=320, ext='.jpg', stretch=False):
        self.stretch = stretch
        self.size = size
        self.ext = ext

    def convert_image(self, path):
        im = Image.open(path).convert("RGB")
        if not self.stretch:
            w, h = im.size
            el = min(im.size)
            box = [
                int((w - el) / 2.),
                int((h - el) / 2.),
                int((w + el) / 2.),
                int((h + el) / 2.),
            ]
            im = im.crop(box)
        im = im.resize((self.size, self.size), Image.ANTIALIAS)

        px = pathlib.Path(path)
        prefix = 'avatar-{0}x{0}.'.format(self.size)
        name = prefix + px.stem + self.ext
        outpath = str(px.with_name(name))
        print(outpath, file=sys.stderr)
        im.save(outpath)

    def batch_convert(self, paths):
        for p in paths:
            self.convert_image(p)


def run(prog=None, args=None):
    import argparse
    desc = 'make avatar'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        '-f', '--format', choices=['jpg', 'png'], default='jpg',
        help='output image format')
    parser.add_argument(
        '-s', '--size', type=int, default=320,
        help='size of output image')
    parser.add_argument(
        '-x', '--stretch', action='store_true',
        help='stretch image to a square (no crop)')
    parser.add_argument(
        'filenames', metavar='FILENAME', nargs='+',
        help='path to an image file')
    ns = parser.parse_args(args)
    ext = '.' + ns.format
    AvatarMaker(ns.size, ext, ns.stretch).batch_convert(ns.filenames)
