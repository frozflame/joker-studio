#!/usr/bin/env python3
# coding: utf-8

from volkanic.cmdline import CommandRegistry

cmddef = """\
avatar      joker.studio.misc.avatar
conv        joker.studio.ffmpeg.conv
crop        joker.studio.ffmpeg.crop
fade        joker.studio.ffmpeg.fade
ico         joker.studio.misc.avatar:mkico
imb         joker.studio.misc.avatar:mkimb
imt         joker.studio.misc.margin
iwh         joker.studio.misc.avatar:report_wh_ratios
poster      joker.studio.ffmpeg.thumb:poster
ren         joker.studio.misc.rename
rotate      joker.studio.images.rotate:main
split       joker.studio.ffmpeg.split
sub         joker.studio.ffmpeg.subtitle
thumb       joker.studio.ffmpeg.thumb:thumb
vid         joker.studio.misc.vident
"""

_prog = "python3 -m joker.studio"
registry = CommandRegistry.from_cmddef(cmddef, _prog)

if __name__ == "__main__":
    registry()
