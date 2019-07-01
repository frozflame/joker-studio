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


def convert_to_ico(path):
    px = pathlib.Path(path).with_suffix('.ico')
    img = Image.open(path)
    img.save(str(px))


def mkico(prog=None, args=None):
    import argparse
    desc = 'convert images to ico format (multiple sizes in 1 file)'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        'filenames', metavar='FILENAME', nargs='+', help='path to images')
    ns = parser.parse_args(args)
    for path in ns.filenames:
        convert_to_ico(path)


def b64enc(path):
    from base64 import b64encode
    return b64encode(open(path, 'rb').read())


def print_bytes(b, width=60, ascode=False):
    n = len(b)
    width = width or n
    ls = [b[i: i + width] for i in range(0, n, width)]
    if not ascode:
        for line in ls:
            print(line.decode())
        return
    s = '_imb = {}'.format(repr(ls[0]))
    sys.stdout.write(s)
    for line in ls[1:]:
        s = ' \\\n       {}'.format(line)
        sys.stdout.write(s)
    sys.stdout.write('\n\n')


def mkimb(prog=None, args=None):
    import argparse
    desc = 'convert a small to base64 encoded bytes'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        '-c', '--code', action='store_true', help='print as code')
    parser.add_argument(
        '-w', '--width', type=int, default=60,
        help='line width (0 for unlimited)')
    parser.add_argument(
        'filename', metavar='FILENAME', help='path to a small image')
    ns = parser.parse_args(args)
    b = b64enc(ns.filename)
    print_bytes(b, ns.width, ns.code)
    if ns.code:
        print('import io, base64; from PIL import Image')
        print('icon = Image.open(io.BytesIO(base64.b64decode(_imb)))')
