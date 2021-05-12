#!/usr/bin/env python3
# coding: utf-8

from volkanic.system import CommandRegistry

entries = {
    'joker.studio.ffmpeg.conv': 'conv',
    'joker.studio.ffmpeg.crop': 'crop',
    'joker.studio.ffmpeg.fade': 'fade',
    'joker.studio.ffmpeg.split': 'split',
    'joker.studio.ffmpeg.subtitle': 'sub',
    'joker.studio.ffmpeg.thumb:thumb': 'thumb',
    'joker.studio.ffmpeg.thumb:poster': 'poster',
    'joker.studio.misc.avatar': 'avatar',
    'joker.studio.misc.avatar:mkico': 'ico',
    'joker.studio.misc.avatar:mkimb': 'imb',
    'joker.studio.misc.avatar:report_wh_ratios': 'iwh',
    'joker.studio.misc.margin': 'imt',
    'joker.studio.misc.rename': 'ren',
    'joker.studio.misc.vident': 'vid',
}

prog = 'python3 -m joker.sudio'
registry = CommandRegistry.from_entries(entries, prog)

if __name__ == '__main__':
    registry()
