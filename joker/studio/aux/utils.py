#!/usr/bin/env python3
# coding: utf-8

import sys
from collections import OrderedDict


def rescale(wsrc, hsrc, w=None, h=None):
    if w is None and h is None:
        w, h = wsrc, hsrc
    elif w is None:
        w = 1. * h * wsrc / hsrc
    elif h is None:
        h = 1. * w * hsrc / wsrc
    return int(w / 2.) * 2, int(h / 2.) * 2


def css_shorthand(*values):
    """css 4-edge shorthand"""
    n = len(values)
    if n <= 1:
        top, right, bottom, left = (list(values) or [0]) * 4
    elif n == 2:
        top = bottom = values[0]
        right = left = values[1]
    elif n == 3:
        top, right, bottom = values
        left = right
    elif n:
        top, right, bottom, left = values
    else:
        raise ValueError('too many values for margins')
    return top, right, bottom, left


def rel_shorthand(width, height, *values):
    """css 4-edge shorthand with fraction support"""
    top, right, bottom, left = css_shorthand(*values)
    top = int(top if top >= 1. else height * top)
    left = int(left if left >= 1. else width * left)
    right = int(right if right >= 1. else width * right)
    bottom = int(bottom if bottom >= 1. else height * bottom)
    return top, right, bottom, left


def split_by_header(s, h):
    return [h + x for x in s.split(h) if x]


def split_stream_png(binstr):
    import io
    from PIL import Image
    h = b'\x89PNG\r\n\x1a\n'
    ims = split_by_header(binstr, h)
    return [Image.open(io.BytesIO(x)) for x in ims]


def add_dry_option(argparser):
    argparser.add_argument(
        '--dry', action='store_true',
        help='print ffmpeg command but do not execute it')


class CommandOptionDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(CommandOptionDict, self).__init__(*args, **kwargs)
        self.pargs = list()
        self.executable = ''

    def as_args(self):
        parts = [self.executable]
        for k, v in self.items():
            if v is None:
                continue
            parts.append('-{}'.format(k))
            if isinstance(v, (tuple, list)):
                parts.extend(v)
            else:
                parts.append(v)
        parts.extend(self.pargs)
        return list(map(str, parts))

    def __str__(self):
        return ' '.join(self.as_args())

    def run(self, dry=False, quiet=False, **kwargs):
        if not quiet:
            print(self, file=sys.stderr)
        if not dry:
            import subprocess
            return subprocess.run(self.as_args(), **kwargs)

    def __call__(self, executable, *pargs):
        # for convenience
        self.executable = executable
        self.pargs = list(pargs)
        return self
