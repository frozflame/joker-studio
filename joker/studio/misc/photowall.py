#!/usr/bin/env python3
# coding: utf-8

import itertools

import numpy
from PIL import Image
from joker.cast.iterative import unflatten
from joker.studio.common.utils import css_shorthand

example_wallspec = {
    "size": (640, 180),
    "frames": [
        {
            "x": 0,
            "y": 0,
            "path": "background.png",
        },
        {
            "x": 3,
            "y": 28,
            "path": "IM001.png",
            "size": (208, 124),
        },
        {
            "x": 216,
            "y": 28,
            "path": "IM002.png",
            "size": (208, 124),
        },
        {
            "x": 428,
            "y": 28,
            "path": "IM002.png",
            "size": (208, 124),
        },
        {
            "x": 0,
            "y": 0,
            "path": "foreground.png",
        },
    ]
}


def make_photowall(wallspec):
    canvas_size = tuple(wallspec['size'])
    canvas = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    for fr in wallspec['frames']:
        im = Image.open(fr['path']).convert("RGBA")
        imsize = tuple(fr.get('size', '')) or canvas_size
        if imsize != im.size:
            im = im.resize(imsize, Image.ANTIALIAS)
        pos = fr['x'], fr['y']
        canvas.paste(im, pos, mask=im)
    return canvas


def make_grid_wallspec(tnsize, repeat, *margins):
    """
    :param tnsize: (int or 2-tuple)
    :param repeat: (int or 2-tuple)
    :param margins: (tuple) handled like css margin property
    :return: (dict) a wallspec
    """
    tnsize = unflatten(tnsize)
    repeat = unflatten(repeat)
    top, right, bottom, left = css_shorthand(*margins)

    xarr = numpy.arange(repeat[0]) * tnsize[0] + left
    yarr = numpy.arange(repeat[-1]) * tnsize[-1] + top
    positions = itertools.product(xarr, yarr)

    tnsize = tnsize[0], tnsize[-1]
    return {
        "frames": [dict(x=x, y=y, size=tnsize) for x, y in positions],
        "size": (
            tnsize[0] * repeat[0] + left + right,
            tnsize[-1] * repeat[-1] + top + bottom,
        )
    }
