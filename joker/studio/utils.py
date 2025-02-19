#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import os
import re

Pathlike = str | os.PathLike[str]


def parse_colon_kv(text: str):
    result = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        line = line.strip()
        key, value = line.split(":", 1)
        result[key.rstrip()] = value.lstrip()
    return result


def sanitize_key(s: str):
    # convert to lowercase and remove non-alphanumeric characters except underscores
    s = s.replace(" ", "_")
    s = re.sub(r"\W+", "", s.lower())
    # if the first character is a number, prepend an underscore
    if s and s[0].isdigit():
        s = "_" + s
    return s
