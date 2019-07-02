#!/usr/bin/env python3
# coding: utf-8
import subprocess
import sys
import traceback

# Two problems to solve
# - play audio fully in terminal
# - play video in fullscreen mode


_cli_players = {
    'audio': [
        {
            'test': ['play', '--version'],
            'mark': 'SoX',
        },
        {
            'test': ['mpv.com', '--version'],
            'mark': 'mplayer',
        },
        {
            'test': ['mpv', '--version'],
            'mark': 'mplayer',
        },
        {
            'test': ['ffplay', '-version'],
            'play': ['ffplay', '-nodisp'],
            'mark': 'ffmpeg',
        },
        {
            'test': ['/Applications/VLC.app/Contents/MacOS/VLC', '--version'],
            'play': ['/Applications/VLC.app/Contents/MacOS/VLC', '-I', 'rc'],
            'mark': 'VLC',
        },
    ],

    'video': [
        {
            'test': ['mpv', '--version'],
            'play': ['mpv', '--fs', '--no-input-default-bindings', '--no-config'],
            'mark': 'mplayer',
        },
        {
            'test': ['/Applications/VLC.app/Contents/MacOS/VLC', '--version'],
            'play': ['/Applications/VLC.app/Contents/MacOS/VLC', '-f'],
            'mark': 'VLC',
        },
        {
            'test': ['ffplay', '-version'],
            'play': ['ffplay', '-fs'],
            'mark': 'ffmpeg',
        },
    ]
}

_available_cli_players = {}


class PlayerNotFoundError(Exception):
    pass


def _find_cli_player(typ):
    for plr in _cli_players[typ]:
        print('debug: typ', typ)
        print('debug: plr', plr)
        try:
            sp = subprocess.run(plr['test'], stdout=subprocess.PIPE)
        except FileNotFoundError:
            continue
        except Exception:
            traceback.print_exc()
            continue
        if sp.returncode:
            continue
        mark = plr['mark']
        outtext = sp.stdout.decode()
        # treat lower-case mark as case-insensitive
        if mark.islower():
            outtext = outtext.lower()
        if mark in outtext:
            return plr
    raise PlayerNotFoundError


def get_cli_player(typ):
    global _available_cli_players
    try:
        return _available_cli_players[typ]
    except KeyError:
        return _available_cli_players.setdefault(typ, _find_cli_player(typ))


def _runsub(*args, **kwargs):
    try:
        subprocess.run(*args, **kwargs)
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt\n', file=sys.stderr)


def _play(path, typ):
    plr = get_cli_player(typ)
    args = plr.get('play') or plr['test'][:1]
    args.append(path)
    _runsub(args)


def play_audio(path):
    _play(path, 'audio')


def play_video(path):
    _play(path, 'video')
