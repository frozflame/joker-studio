#!/usr/bin/env python3
# coding: utf-8

import pathlib
import sys

from PIL import Image
from joker.cast.iterative import chunkwize_split


class AvatarMaker(object):
    def __init__(self, size=320, ext=".jpg", stretch=False):
        self.stretch = stretch
        self.size = size
        self.ext = ext

    def convert_image(self, path):
        im = Image.open(path).convert("RGB")
        if not self.stretch:
            w, h = im.size
            el = min(im.size)
            box = [
                int((w - el) / 2.0),
                int((h - el) / 2.0),
                int((w + el) / 2.0),
                int((h + el) / 2.0),
            ]
            im = im.crop(box)
        im = im.resize((self.size, self.size), Image.ANTIALIAS)

        px = pathlib.Path(path)
        prefix = "avatar-{0}x{0}.".format(self.size)
        name = prefix + px.stem + self.ext
        outpath = str(px.with_name(name))
        print(outpath, file=sys.stderr)
        im.save(outpath)

    def batch_convert(self, paths):
        for p in paths:
            self.convert_image(p)


def run(prog=None, args=None):
    import argparse

    desc = "make avatar"
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        "-f",
        "--format",
        choices=["jpg", "png"],
        default="jpg",
        help="output image _format",
    )
    parser.add_argument(
        "-s", "--size", type=int, default=320, help="size of output image"
    )
    parser.add_argument(
        "-x",
        "--stretch",
        action="store_true",
        help="stretch image to a square (no crop)",
    )
    parser.add_argument(
        "filenames", metavar="FILENAME", nargs="+", help="path to an image file"
    )
    ns = parser.parse_args(args)
    ext = "." + ns.format
    AvatarMaker(ns.size, ext, ns.stretch).batch_convert(ns.filenames)


def convert_to_ico(path):
    px = pathlib.Path(path).with_suffix(".ico")
    img = Image.open(path)
    img.save(str(px))


def mkico(prog=None, args=None):
    import argparse

    desc = "convert images to ico _format (multiple sizes in 1 file)"
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        "filenames", metavar="FILENAME", nargs="+", help="path to images"
    )
    ns = parser.parse_args(args)
    for path in ns.filenames:
        convert_to_ico(path)


def b64enc(path):
    from base64 import b64encode

    return b64encode(open(path, "rb").read())


class SmallImage(object):
    def __init__(self, binstr, fmt):
        fmt = fmt.lower()
        self._binstr = binstr
        self._format = {"jpg": "jpeg"}.get(fmt, fmt)

    @classmethod
    def from_file(cls, path, fmt=None):
        binstr = open(path, "rb").read()
        fmt = fmt or path.split(".")[-1]
        return cls(binstr, fmt)

    def b64encode(self):
        from base64 import b64encode

        return b64encode(self._binstr)

    def b64s(self):
        from base64 import b64encode

        return b64encode(self._binstr).decode()

    def html_tag(self):
        return '<img src="data:image/png;base64, {}" alt=""/>'.format(self.b64s())

    def pycode(self, width=60):
        pieces = chunkwize_split(width, self.b64encode())
        notations = (repr(s) for s in pieces)
        prefix = "_imb = "
        sep = " \\\n" + " " * len(prefix)
        parts = [
            prefix + sep.join(notations),
            "import io, base64; from PIL import Image",
            "icon = Image.open(io.BytesIO(base64.b64decode(_imb)))",
        ]
        return "\n\n".join(parts)


def mkimb(prog=None, args=None):
    import argparse

    desc = "Convert an image to base64 encoded bytes"
    parser = argparse.ArgumentParser(prog=prog, description=desc)

    parser.add_argument(
        "-s",
        "--style",
        choices=["py", "html"],
        help="print as python code or html img tag",
    )

    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=60,
        help="line width (0 for unlimited, N/A when style=html)",
    )

    parser.add_argument("filename", metavar="FILENAME", help="path to a small image")

    ns = parser.parse_args(args)
    si = SmallImage.from_file(ns.filename)
    if not ns.style:
        parts = chunkwize_split(ns.width, si.b64s())
        print("\n".join(parts))
    elif ns.style == "py":
        print(si.pycode(ns.width))
    elif ns.style == "html":
        print(si.html_tag())


def _average(nums):
    return sum(nums) / len(nums)


def report_wh_ratios(_, args: list):
    from joker.studio.aux.info import MediaInfo

    ratios = []
    widths = []
    heights = []
    for path in args:
        xinfo = MediaInfo(path)
        w = xinfo.image.width
        h = xinfo.image.height
        r = w / h
        print("{:.03f}".format(r), w, h, path)
        ratios.append(r)
        widths.append(w)
        heights.append(h)
    avg_r = _average(ratios)
    avg_w = int(_average(widths))
    avg_h = int(_average(heights))
    print("{:.03f}".format(avg_r), avg_w, avg_h, "<avg>")
