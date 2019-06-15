#!/usr/bin/env python3
# coding: utf-8

import argparse
import math
import pathlib

from joker.studio.common import utils
from joker.studio.common.info import MediaInfo


def _labelfunc(startpos, duration, step):
    m, s = divmod(startpos, 60)
    h, m = divmod(m, 60)
    hh = '{:02}'.format(h) if duration >= 3600 else ''
    mm = '{:02}'.format(m)
    ss = '{:02}'.format(s) if step % 60 else 'M'
    return hh + mm + ss


def uniform_split(ns):
    """
    :param ns: an argparse.Namespace obj
    :return: a generator of CommandOptionDict instances
    """
    xinfo = MediaInfo(ns.path)
    duration = math.ceil(xinfo.get_video_duration())
    step = duration / ns.num if ns.num else ns.step
    step = math.ceil(step)
    px = pathlib.Path(ns.path)

    for startpos in range(0, duration, step):
        cod = utils.CommandOptionDict([
            ('i', ns.path),
            ('ss', startpos),
            ('t', step),
            ('c:v', 'copy'),
            ('c:a', 'copy'),
        ])

        suffix = '._split_' + _labelfunc(startpos, duration, step) + px.suffix
        yield cod('ffmpeg', px.with_suffix(suffix))


def run(prog=None, args=None):
    desc = 'split a video uniformly'
    parser = argparse.ArgumentParser(prog=prog, description=desc)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-s', '--step', type=int, default=240,
        help='length of each segment, in second')
    group.add_argument(
        '-n', '--num', type=int,
        help='number of segments to split into')

    parser.add_argument(
        'path', metavar='string', help='a video')

    utils.add_dry_option(parser)
    ns = parser.parse_args(args)
    print(vars(ns))
    for cod in uniform_split(ns):
        cod.run(ns.dry)


if __name__ == '__main__':
    run()
