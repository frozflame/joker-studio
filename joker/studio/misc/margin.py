#!/usr/bin/env python3
# coding: utf-8
import argparse
import os
import pathlib

import numpy
from PIL import Image
from joker.cast.syntax import printerr

STDMAX = 3


def get_corner_size(arr):
    n = sum(arr.shape[:2]) / 8.
    return int(n ** .5)


class MarginDetection(object):
    def __init__(self, img, stdmax=STDMAX):
        self.img = img.convert('RGB')
        self.arr = numpy.asarray(self.img).astype('uint32')
        self.maxstd = stdmax
        n = get_corner_size(self.arr)
        _sli_head = slice(None, n)
        _sli_tail = slice(-n, None)
        corner_pixels = numpy.stack((
            self.arr[_sli_head, _sli_head, :],
            self.arr[_sli_head, _sli_tail, :],
            self.arr[_sli_tail, _sli_tail, :],
            self.arr[_sli_head, _sli_tail, :],
        ), axis=0).reshape(-1, 3)
        # printerr(corner_pixels.shape)
        # raise ValueError

        if not self._check_std(corner_pixels):
            raise ValueError('standard variance is too large')

        arr = self.arr
        yi = self._measure(arr, corner_pixels)
        yo = arr.shape[0] - self._measure(arr[::-1, :, :], corner_pixels)

        arr = self.arr.transpose((1, 0, 2))
        xi = self._measure(arr, corner_pixels)
        xo = arr.shape[0] - self._measure(arr[::-1, :, :], corner_pixels)
        self.box = xi, yi, xo, yo

    @classmethod
    def from_file(cls, path, stdmax=STDMAX):
        return cls(Image.open(path), stdmax)

    def crop(self, outpath=''):
        cimg = self.img.crop(self.box)
        if outpath:
            cimg.save(outpath)
        return cimg

    def _check_std(self, pixels):
        if any(list(pixels.std(axis=0) > self.maxstd)):
            return False
        return True

    def _measure(self, arr, corner_pixels):
        """
        :param arr: W x H x 3
        :param corner_pixels: ? x 3
        :return:
        """
        for i in range(arr.shape[0]):
            line = arr[i, :, :]
            line.shape = -1, 3
            pixels = numpy.concatenate((line, corner_pixels), axis=0)
            if not self._check_std(pixels):
                return i
        return 0


def margin_crop(path, prefix, stdmax):
    px = pathlib.Path(path)
    if px.name.startswith(prefix):
        raise ValueError('input file named with output prefix')
    px_out = px.with_name(prefix + px.name)
    if px_out.exists():
        raise IOError('output file exists')
    mdet = MarginDetection.from_file(path, stdmax)
    mdet.crop(px_out)


def run(prog=None, args=None):
    desc = 'Crop images with homogeneously colored margins'
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    default_prefix = prog.upper().split()[-1] + '.'
    pr.add_argument('-s', '--stdmax', default=STDMAX, type=int,
                    help='maximum standard deviation')
    pr.add_argument('-p', '--prefix', default=default_prefix,
                    help='name prefix for generated files')
    pr.add_argument('-D', '--delete', action='store_true',
                    help='delete original files')
    pr.add_argument('files', nargs='*', metavar='PATH',
                    help='paths to files to be cropped')
    ns = pr.parse_args(args)
    for path in ns.files:
        try:
            margin_crop(path, ns.prefix, ns.stdmax)
        except Exception as e:
            printerr('Failed:', path, '--', e)
            continue
        if ns.delete:
            os.remove(path)
