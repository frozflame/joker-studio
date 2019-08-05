#!/usr/bin/env python3
# coding: utf-8

import sys

from joker.textmanip.main import registry

registry(['python3 -m joker.sudio'] + sys.argv[1:])
