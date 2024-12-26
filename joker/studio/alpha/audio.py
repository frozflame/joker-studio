#!/usr/bin/env python3
# coding: utf-8

import os
import re
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile


def read_audio(path):
    if path.endswith(".wav"):
        return wavfile.read(path)
    tmp = tempfile.mkstemp()[1]
    cmd = ["ffmpeg", "-y", "-i", path, "-f", "wav", tmp]
    try:
        subprocess.run(cmd)
        return wavfile.read(tmp)
    finally:
        os.remove(tmp)


def chop(arr, winsize):
    assert arr.ndim == 1
    n = len(arr)
    arr = arr[: n - n % winsize]
    arr.shape = -1, winsize
    return arr.mean(axis=1)


def compute_audio_energy_string(path):
    if path.endswith(".wav"):
        sample_rate, data = wavfile.read(path)
    else:
        sample_rate, data = read_audio(path)

    # merge 2 channels, and limit value to exp(10)-1
    data = np.abs(data).max(axis=1)

    # 0.1 second pieces
    data = chop(data, int(sample_rate * 0.1))
    data = np.log2(1.0 + data) / 1.501
    data = data.astype(int)
    return "".join(format(i, "X") for i in data)


class AudioEnergySeries(object):
    def __init__(self, levels, winsize):
        self._levels = np.array(levels, dtype="uint8")
        self._string = "".join(format(i, "X") for i in self._levels)
        self._winsize = winsize

    def __str__(self):
        return self._string

    @classmethod
    def from_file(cls, path, winsize=0.1):
        sample_rate, data = read_audio(path)

        # merge 2 channels, and limit value to exp(10)-1
        data = np.abs(data).max(axis=1)

        # 0.1 second pieces
        data = chop(data, int(sample_rate * 0.1))
        data = np.log2(1.0 + data) / 1.501
        return cls(data, winsize)

    def find_silences(self, thresh=3, duration=1):
        assert 0 <= thresh <= 9
        n = round(duration / self._winsize)
        pat = r"[0-%d]{%d,}" % (thresh, n)
        for mat in re.finditer(pat, self._string):
            yield sum(mat.span()) / 2.0 * self._winsize
