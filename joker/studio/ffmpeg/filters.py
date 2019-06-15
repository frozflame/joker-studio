#!/usr/bin/env python3
# coding: utf-8

from joker.studio.common.utils import rel_shorthand


def vf_crop(width, height, *margins):
    top, right, bottom, left = rel_shorthand(width, height, *margins)
    ow = width - left - right
    oh = height - top - bottom
    return 'crop={}:{}:{}:{}'.format(ow, oh, left, top)


def vf_subtitle(path, styles):
    if not styles:
        return 'subtitles=' + path
    if isinstance(styles, dict):
        styles = styles.items()
    stl = ','.join('{}={}'.format(*p) for p in styles)
    return "subtitles={}:force_style='{}'".format(path, stl)


def af_fade(cutin, cutout, fadein, fadeout):
    """
    :param cutin: (number) position in the original audio where segment starts
    :param cutout: (number) position in the original audio where segment ends
    :param fadein: (number) length of audio where fade-in applied, in sec
    :param fadeout: (number) length of audio where fade-out applied, in sec
    :return: (str) ffmpeg audio filter string
    """
    a = cutin, fadein, cutout - fadeout, fadeout
    return 'afade=t=in:st={}:d={},afade=t=out:st={}:d={}'.format(*a)
