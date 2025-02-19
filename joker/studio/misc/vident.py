#!/usr/bin/env python3
# coding: utf-8
import argparse
import os
import re
import sys
import traceback
from collections import defaultdict

from joker.cast.syntax import printerr
from joker.cast.timedate import sexagesimal_format, sexagesimal_parse
from joker.textmanip.path import proper_filename

from joker.studio.aux.info import MediaInfo
from joker.studio.misc.rename import compute_video_hash


class VideoIdentifier(object):
    version = "vid4_"
    __slots__ = ["duration", "vhash", "w", "h"]

    def __init__(self, duration, vhash, width, height):
        self.duration = duration
        self.vhash = vhash
        self.w = int(width)
        self.h = int(height)

    def __str__(self):
        return "{}-{}x{}".format(self.unikey, self.w, self.h)

    @property
    def unikey(self):
        ds = sexagesimal_format(int(self.duration))
        ds = ds.rjust(3, "0")
        return self.version + "{}_{}".format(ds, self.vhash)

    @classmethod
    def get_regex(cls):
        p = "^" + VideoIdentifier.version
        return re.compile(p + r"([0-9a-yA-Y]{,4})_([0-9A-Z]{,80})-(\d+)x(\d+)")

    @classmethod
    def parse(cls, string):
        mat = cls.get_regex().match(string)
        if mat is None:
            msg = "bad identifier string: {}".format(repr(string))
            raise ValueError(msg)
        ds, fc, w, h = mat.groups()
        return cls(sexagesimal_parse(ds), fc, w, h)

    @classmethod
    def from_name(cls, path):
        xinfo = MediaInfo(path)
        duration = xinfo.get_video_duration()
        vh = compute_video_hash(path)
        v = xinfo.video
        return cls(duration, vh, v.width, v.height)

    @classmethod
    def make_name(cls, path):
        dir_, name = os.path.split(path)
        if name.startswith(cls.version):
            vident = cls.parse(name.split(".")[0])
            return vident, path

        vident = cls.from_name(path)
        new_name = "{}.{}".format(vident, proper_filename(name))
        new_path = os.path.join(dir_, new_name)
        return vident, new_path

    @classmethod
    def rename(cls, path):
        vident, new_path = cls.make_name(path)
        if new_path != path:
            print("new_path:", new_path, file=sys.stderr)
            os.rename(path, new_path)
        return vident, new_path


def p_filter_by_extension(paths):
    extensions = {".mp4", ".ts", ".mkv"}
    _splitext = os.path.splitext
    return [p for p in paths if _splitext(p)[1] in extensions]


def p_filter_by_prefix(paths):
    vp = VideoIdentifier.version
    _split = os.path.split
    return [p for p in paths if _split(p)[1].startswith(vp)]


def keyfunc(pair):
    vi, path = pair
    return vi.w, path.endswith(".mp4")


def show(paths):
    for path in paths:
        try:
            vi = VideoIdentifier.from_name(path)
            print(vi, path, sep="\t")
        except Exception as e:
            # printerr(e)
            traceback.print_exc()
            printerr("bad file:", path)


def add_vident_prefix(paths):
    groups = defaultdict(list)
    for path in p_filter_by_extension(paths):
        try:
            vi, path = VideoIdentifier.rename(path)
        except ValueError:
            traceback.print_exc()
            printerr("bad file:", path)
            continue
        groups[vi.unikey].append((vi, path))

    for pairs in groups.values():
        if len(pairs) < 2:
            continue
        pairs.sort(key=keyfunc, reverse=True)
        print("\n#    ", pairs[0][1])
        for _, path in pairs[1:]:
            print("rm -f", path)


def remove_vident_prefix(paths):
    paths = p_filter_by_extension(paths)
    for path in p_filter_by_prefix(paths):
        dir_, name = os.path.split(path)
        regex = VideoIdentifier.get_regex()
        new_name = regex.sub("", name)
        if new_name.startswith("."):
            new_name = new_name[1:]
        new_path = os.path.join(dir_, new_name)
        if new_name and not os.path.exists(new_path):
            os.rename(path, new_path)
        else:
            printerr("cannot rename:")
            printerr(' from "{}"'.format(path))
            printerr('   to "{}"'.format(new_path))


def run(prog=None, args=None):
    desc = "rename video files by adding or removing video identifier"
    parser = argparse.ArgumentParser(prog=prog, description=desc)

    # mutually exclusive
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-a",
        "--add-prefix",
        action="store_true",
        help="rename with vident prefix",
    )
    group.add_argument(
        "-r",
        "--remove-prefix",
        action="store_true",
        help="rename with vident prefix removed",
    )
    parser.add_argument("paths", metavar="PATH", nargs="+", help="files")
    ns = parser.parse_args(args)
    if ns.add_prefix:
        add_vident_prefix(ns.paths)
    elif ns.remove_prefix:
        remove_vident_prefix(ns.paths)
    else:
        show(ns.paths)


if __name__ == "__main__":
    run()
