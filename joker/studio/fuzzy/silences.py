#!/usr/bin/env python3
# coding: utf-8

import os
import re
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile

DIVSEC = 10


def chop(arr, w):
    assert arr.ndim == 1
    n = len(arr)
    arr = arr[:n - n % w]
    arr.shape = -1, w
    return arr.mean(axis=1).astype(int)


def to_bytes(arr):
    mx = np.max(arr)
    arr = arr.astype(float)
    arr /= mx / 100.
    return arr.astype('uint8').tobytes()


def _read_audio(path):
    tmp = tempfile.mkstemp()[1]
    cmd = ["ffmpeg", "-y", "-i", path, "-f", "wav", tmp]
    try:
        subprocess.run(cmd)
        return wavfile.read(tmp)
    finally:
        os.remove(tmp)


def find_silences(path):
    if path.endswith('.wav'):
        sample_rate, data = wavfile.read(path)
    else:
        sample_rate, data = _read_audio(path)

    # merge 2 channels
    data = np.abs(data).mean(axis=1)

    # 0.1 second pieces
    data = chop(data, int(sample_rate / DIVSEC))

    binstr = to_bytes(data)
    regex = re.compile(b'\0' * DIVSEC + b'+')
    positions = []
    for m in regex.finditer(binstr):
        pos = sum(m.span()) / 2 / DIVSEC
        positions.append(int(pos))
    return positions
