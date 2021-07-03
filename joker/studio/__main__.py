#!/usr/bin/env python3
# coding: utf-8

from volkanic.system import CommandRegistry

cmddef = """\
conv        joker.studio.ffmpeg.conv
crop        joker.studio.ffmpeg.crop
fade        joker.studio.ffmpeg.fade
split       joker.studio.ffmpeg.split
sub         joker.studio.ffmpeg.subtitle
thumb       joker.studio.ffmpeg.thumb:thumb
poster      joker.studio.ffmpeg.thumb:poster
avatar      joker.studio.misc.avatar
ico         joker.studio.misc.avatar:mkico
imb         joker.studio.misc.avatar:mkimb
iwh         joker.studio.misc.avatar:report_wh_ratios
imt         joker.studio.misc.margin
ren         joker.studio.misc.rename
vid         joker.studio.misc.vident
"""

_prog = 'python3 -m joker.sudio'
registry = CommandRegistry.from_cmddef(cmddef, _prog)

if __name__ == '__main__':
    registry()
