#!/usr/bin/env python3
# coding: utf-8

from volkanic.system import CommandRegistry

entries = {
    'joker.studio.ffmpeg.crop': 'crop',
    'joker.studio.ffmpeg.fade': 'fade',
    'joker.studio.ffmpeg.split': 'split',
    'joker.studio.ffmpeg.convert': 'conv',
    'joker.studio.ffmpeg.thumbnail': 'thumbnail',
    'joker.studio.ffmpeg.thumbnail:run_poster': 'poster',
    'joker.studio.misc.avatar': 'avatar',
}

registry = CommandRegistry(entries)

if __name__ == '__main__':
    registry()
