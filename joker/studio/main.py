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
    'joker.studio.misc.margin': 'imt',
    'joker.studio.misc.remove': 'rmdir',
    'joker.studio.misc.rename': 'ren',
    'joker.studio.misc.vident': 'vid',
}

registry = CommandRegistry(entries)

if __name__ == '__main__':
    registry()
