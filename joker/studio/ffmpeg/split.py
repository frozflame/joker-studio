#!/usr/bin/env python3
# coding: utf-8


import argparse
import math

import os
from joker.studio.common.info import MediaInfo
from joker.studio.common.utils import CommandOptionDict


def _labelfunc(seconds, inminute=False):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if inminute:
        return 'M{:02}{:02}'.format(h, m)
    else:
        return '{:02}{:02}{:02}'.format(h, m, s)


def uniform_split(path, step, length):
    """
    :param path: (str)
    :param step: (int) in second
    :param length: (int) in second
    :return: a generator of CommandOptionDict instances
    """
    xinfo = MediaInfo(path)
    duration = math.ceil(xinfo.get_audio_duration())
    inminute = not (step % 60 or length % 60)
    for startpos in range(0, duration, step):
        cod = CommandOptionDict([
            ('i', path),
            ('ss', startpos),
            ('t', length),
            ('c:v', 'copy'),
            ('c:a', 'copy'),
        ])
        bx = os.path.splitext(path)
        label = '.Split' + _labelfunc(startpos, inminute)
        outpath = bx[0] + label + bx[1]
        yield cod('ffmpeg', outpath)


# TODO: add 2nd mod: given num of pieces, divide evenly
def run(prog=None, args=None):
    desc = 'split a video uniformly'
    parser = argparse.ArgumentParser(prog=prog, description=desc)

    parser.add_argument(
        '-s', '--step', type=int, default=240, help='in second')

    parser.add_argument(
        '-l', '--length', type=int, default=240, help='in second')

    parser.add_argument(
        '--dry', action='store_true',
        help='print ffmpeg command but do not execute it')

    parser.add_argument(
        'path', metavar='string', help='a video')

    ns = parser.parse_args(args)
    for cod in uniform_split(ns.path, ns.step, ns.length):
        cod.run(ns.dry)


if __name__ == '__main__':
    run()
