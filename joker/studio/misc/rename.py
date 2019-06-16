#!/usr/bin/env python3
# coding: utf-8

import argparse
import hashlib
import os
import pathlib
import re

from joker.studio.common.info import MediaInfo

extcorrection = {
    '.jpeg': '.jpg',
    '.mpeg': '.mpg',
    '.tiff': '.tif',
    '.png_large': '.png',
    '.jpg_large': '.jpg',
    '.bmp_large': '.bmp',
}

extmap = {
    'audio': ['.mp3', '.wav', '.aac', '.ogg', '.wma', '.flac'],
    'image': ['.jpg', '.bmp', '.png', '.png_large', '.jpg_large', '.gif'],
    'video': ['.mp4', '.mkv', '.flv', '.wmv', '.mov', '.rmvb', '.ts'],
}

iextmap = dict()
for _category, _extensions in extmap.items():
    for _ext in _extensions:
        iextmap[_ext] = _category


class MediaRenameTask(object):
    def __init__(self, path):
        self.px = self.clean(path)
        self.path = path
        self.xinfo = MediaInfo(path)

    @staticmethod
    def clean(path):
        px = pathlib.Path(path)
        stem = px.stem
        stem = re.sub(r'[.\s]+', '.', stem)
        stem = re.sub(r'\.$', '', stem)
        ext = px.suffix.lower()
        ext = extcorrection.get(ext, ext)
        return px.with_name(stem + ext)

    def __call__(self):
        new_path = str(self.px)
        if self.path != new_path:
            os.rename(self.path, new_path)
        return new_path

    def audio(self):
        # remove existing Dur71s:
        stem = re.sub(r'\.Dur\d+s\b', '', self.px.stem)
        duration = self.xinfo.get_audio_duration()
        if duration:
            stem += '.Dur{:.0f}s'.format(duration)
        self.px = self.px.with_name(stem + self.px.suffix)
        return self

    def image(self):
        # remove existing 640x480
        stem = re.sub(r'\.\d+x\d+\b', '', self.px.stem)
        img = self.xinfo.image
        stem += '.{}x{}'.format(img.width, img.height)
        self.px = self.px.with_name(stem + self.px.suffix)
        return self

    def video(self):
        # remove Dur71s and 640x480
        stem = re.sub(r'\.Dur\d+s\b', '', self.px.stem)
        stem = re.sub(r'\.\d+x\d+\b', '', stem)
        vid = self.xinfo.video
        stem += '{}x{}'.format(vid.width, vid.height)
        duration = self.xinfo.get_video_duration()
        if duration:
            stem += '.Dur{:.0f}s'.format(duration)
        self.px = self.px.with_name(stem + self.px.suffix)
        return self

    @classmethod
    def rename_a_file(cls, path):
        rentask = cls(path)
        ext = rentask.px.suffix
        if iextmap.get(ext.lower()) == 'audio':
            return rentask.audio()()
        if iextmap.get(ext.lower()) == 'image':
            return rentask.image()()
        if iextmap.get(ext.lower()) == 'video':
            return rentask.video()()
        return rentask()


def run(prog=None, args=None):
    """entry for media file rename"""
    desc = 'rename files'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        'paths', metavar='PATH', nargs='+', help='files')
    ns = parser.parse_args(args)
    for p in ns.paths:
        MediaRenameTask.rename_a_file(p)


class SerialRenamer(object):
    def __init__(self, start):
        self.serial = start

    @staticmethod
    def compute_hash(path, algor='md5'):
        chunksize = 1024
        hashfunc = hashlib.new(algor)
        with open(path, 'rb') as fin:
            chunk = fin.read(chunksize)
            while chunk:
                hashfunc.update(chunk)
                chunk = fin.read(chunksize)
        return hashfunc.hexdigest()

    def make_affix(self, typ, path):
        if typ in hashlib.algorithms_guaranteed:
            return self.compute_hash(path, typ)
        elif typ == 'serial':
            return '{:03}'.format(self.serial)

    @classmethod
    def rename_files(cls, ns):
        sr = cls(ns.start)
        for ix, path in enumerate(ns.files):
            px = pathlib.Path(path)
            prefix = sr.make_affix(ns.prefix, path)
            infix = sr.make_affix(ns.infix, path)
            parts = [prefix, ns.stem or px.stem, infix]
            ext = px.suffix.lower()
            ext = extcorrection.get(ext, ext)
            name = '.'.join([x for x in parts if x]) + ext
            new_px = px.with_name(name)
            px.rename(new_px)


def run_rens(prog=None, args=None):
    desc = 'rename files with their hashes and serial nums'
    choices = ['serial', 'md5', 'sha1', 'sha256', 'sha512']
    affix_help = 'a hash algorithm or "serial"'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument(
        '-p', '--prefix', default='serial', choices=choices, help=affix_help)
    parser.add_argument(
        '-i', '--infix', default='md5', choices=choices, help=affix_help)
    parser.add_argument(
        '-m', '--stem', help='replace original stem with')
    parser.add_argument(
        '-s', '--start', default=101, type=int, help='an integer')
    parser.add_argument(
        'files', metavar='PATH', nargs='+', help='files')
    ns = parser.parse_args(args)
    SerialRenamer.rename_files(ns)
