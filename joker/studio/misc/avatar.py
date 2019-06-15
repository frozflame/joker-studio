#!/usr/bin/env python3
# coding: utf-8

import os

from PIL import Image


class AvatarMaker(object):
    def __init__(self, size=160, ext='.jpg'):
        self.size = size
        self.ext = ext

    def make_filename(self, name):
        base, _ = os.path.splitext(name)
        dimension = '.{0}x{0}'.format(self.size)
        return base + dimension + self.ext

    def convert_image(self, path):
        im = Image.open(path).convert("RGB")
        im = im.resize((self.size, self.size))
        im.save(self.make_filename(path))

    @classmethod
    def batch_convert(cls, size, ext, paths):
        conv = cls(size, ext)
        for p in paths:
            conv.convert_image(p)


def run(prog=None, args=None):
    import argparse
    desc = 'make avatar'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        '-f', '--format', choices=['jpg', 'png'], default='jpg',
        help='output image format')
    parser.add_argument(
        '-s', '--size', type=int, default=160,
        help='size of output image')
    parser.add_argument(
        'filenames', metavar='FILENAME', nargs='+',
        help='path to an image file')
    ns = parser.parse_args(args)
    ext = '.' + ns.format
    AvatarMaker.batch_convert(ns.size, ext, ns.filenames)

