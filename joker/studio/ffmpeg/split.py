#!/usr/bin/env python3
# coding: utf-8

import argparse
import math
import pathlib

from joker.studio.aux import utils
from joker.studio.aux.info import MediaInfo


def _labelfunc(startpos, duration, step):
    m, s = divmod(startpos, 60)
    h, m = divmod(m, 60)
    hh = '{:02}'.format(h) if duration >= 3600 else ''
    mm = '{:02}'.format(m)
    ss = '{:02}'.format(s) if step % 60 else 'M'
    return hh + mm + ss


class MediaSplitter(object):
    def __init__(self, path):
        self.px = pathlib.Path(path)
        self.path = path
        self.xinfo = MediaInfo(path)
        self.duration = math.ceil(self.xinfo.get_duration())

    def _fmt_label(self, startpos, precise=True):
        m, s = divmod(startpos, 60)
        h, m = divmod(m, 60)
        hh = '{:02}'.format(h) if self.duration >= 3600 else ''
        mm = '{:02}'.format(m)
        ss = '{:02}'.format(s) if precise else 'M'
        return hh + mm + ss

    def split(self, position_pairs):
        position_pairs = list(position_pairs)
        precise = any(pair[0] % 60 for pair in position_pairs)
        for start, length in position_pairs:
            cod = utils.CommandOptionDict([
                ('i', self.px),
                ('ss', start),
                ('t', length),
                ('c:v', 'copy'),
                ('c:a', 'copy'),
            ])
            label = '.SPLIT-' + self._fmt_label(start, precise)
            px_out = self.px.with_suffix(label + self.px.suffix)
            yield cod('ffmpeg', px_out)

    def uniform_split(self, step):
        # step = duration / num if num else ns.step
        step = math.ceil(step)
        start_positions = range(0, self.duration, step)
        return self.split((p, step) for p in start_positions)

    def custom_split(self, positions):
        positions = list(positions)
        positions.sort()
        if positions[0] != 0:
            positions.insert(0, 0)
        if positions[-1] < self.duration:
            positions.append(self.duration)
        pairs = zip(positions[:-1], positions[1:])
        return self.split(pairs)

    def silence_split(self):
        from joker.studio.fuzzy.silences import find_silences
        return self.custom_split(find_silences(self.path))


def run(prog=None, args=None):
    desc = 'Split a video uniformly or at specified positions'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    utils.add_dry_option(parser)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-n', '--num', type=int, metavar='INT',
        help='number of segments to split into')
    group.add_argument(
        '-s', '--step', type=int, default=240, metavar='INT',
        help='length of each segment, in second')
    group.add_argument(
        '-p', '--positions', type=int, nargs='+',
        metavar='INT', help='positions of splits')
    group.add_argument(
        '-q', '--silence', action='store_true',
        help='split on silences')

    parser.add_argument('path', help='a video or audio file')
    ns = parser.parse_args(args)
    mspl = MediaSplitter(ns.path)
    if ns.silence:
        cods = mspl.silence_split()
    elif ns.positions:
        cods = mspl.custom_split(ns.positions)
    else:
        step = mspl.duration / ns.num if ns.num else ns.step
        cods = mspl.uniform_split(step)
    for cod in cods:
        cod.run(ns.dry)


if __name__ == '__main__':
    run()
