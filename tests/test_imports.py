#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import importlib
import json
import re

import setuptools
from volkanic.introspect import find_all_plain_modules
from volkanic.utils import printerr

from joker.studio.environ import GlobalInterface

gi = GlobalInterface()

dotpath_prefixes = [
    "joker.",
    # 'tests.',
]


def test_json_integrity():
    for path in gi.project_dir.rglob("*.json"):
        print("checking json file", path)
        json.load(path.open())


def _check_prefix(path):
    for prefix in dotpath_prefixes:
        if path.startswith(prefix):
            return True
    return False


def test_module_imports():
    pdir = gi.under_project_dir()
    for dotpath in find_all_plain_modules(pdir):
        if _check_prefix(dotpath):
            print("importing", dotpath)
            importlib.import_module(dotpath)


def read_all_py_files():
    pdir = gi.under_project_dir()
    for path in setuptools.findall(pdir):
        if not path.endswith(".py"):
            continue
        for idx, line in enumerate(open(path)):
            line = line.strip()
            if not line:
                continue
            yield path, idx, line


if __name__ == "__main__":
    test_module_imports()
    test_json_integrity()
