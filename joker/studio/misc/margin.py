#!/usr/bin/env python3
# coding: utf-8
import argparse
import pathlib

import numpy
from PIL import Image
from joker.cast.syntax import printerr

STDMAX = 3


def get_corner_size(arr):
    n = sum(arr.shape[:2]) / 8.0
    return int(n**0.5)


class MarginDetection(object):
    def __init__(self, img, stdmax=STDMAX):
        self.img = img.convert("RGB")
        self.arr = numpy.asarray(self.img).astype("uint32")
        self.maxstd = stdmax
        n = get_corner_size(self.arr)
        _sli_head = slice(None, n)
        _sli_tail = slice(-n, None)
        corner_pixels = numpy.stack(
            (
                self.arr[_sli_head, _sli_head, :],
                self.arr[_sli_head, _sli_tail, :],
                self.arr[_sli_tail, _sli_tail, :],
                self.arr[_sli_head, _sli_tail, :],
            ),
            axis=0,
        ).reshape(-1, 3)
        # printerr(corner_pixels.shape)
        # raise ValueError

        if not self._check_std(corner_pixels):
            raise ValueError("standard variance is too large")

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

    def crop(self):
        return self.img.crop(self.box)

    def save(self, outpath):
        return self.crop().save(outpath)

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


def _backup(path):
    px = pathlib.Path(path)
    for i in range(100):
        tag = ".ORIG-{:02}".format(i)
        px_bak = px.with_suffix(tag + px.suffix)
        if not px_bak.exists():
            return px.rename(px_bak)


def margin_crop(path, stdmax, backup=True):
    mdet = MarginDetection.from_file(path, stdmax)
    backup and _backup(path)
    mdet.save(path)


def run(prog=None, args=None):
    desc = "Crop images with homogeneously colored margins "
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    pr.add_argument(
        "-s", "--stdmax", default=STDMAX, type=int, help="maximum standard deviation"
    )
    pr.add_argument(
        "-B", "--no-backup", action="store_true", help="do NOT backup original file"
    )
    pr.add_argument(
        "files", nargs="*", metavar="PATH", help="paths to files to be cropped"
    )
    ns = pr.parse_args(args)
    for path in ns.files:
        try:
            margin_crop(path, ns.stdmax, not ns.no_backup)
        except Exception as e:
            printerr("Failed:", path, "--", e)
            continue
