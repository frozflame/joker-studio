#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from joker.studio.utils import parse_colon_kv, sanitize_key, Pathlike


def run_tesseract_osd_only(path: Pathlike) -> dict:
    cmd = [
        "tesseract",
        path,
        "-",
        "--psm",
        "0",
    ]
    subp = subprocess.run(cmd, capture_output=True)
    s = subp.stdout.decode("utf-8")
    return {sanitize_key(k): v for k, v in parse_colon_kv(s).items()}


def infer_rotation_degrees(path: Pathlike) -> int:
    osd_dict = run_tesseract_osd_only(path)
    return int(osd_dict.get("rotate", 0))


def _get_output_path(path: Pathlike):
    path = Path(path).absolute()
    infix = os.urandom(8).hex()
    return path.with_stem(f"{path.stem}-{infix}")


def rotate_image(path: Pathlike, overwrite=False) -> Path | None:
    degrees = infer_rotation_degrees(path)
    if not degrees:
        return None
    if overwrite:
        outpath = path
        cmd = [
            "magick",
            "mogrify",
            "-rotate",
            degrees,
            outpath,
        ]
    else:
        outpath = _get_output_path(path)
        cmd = [
            "magick",
            path,
            "-rotate",
            degrees,
            outpath,
        ]
    subprocess.run([str(s) for s in cmd])
    return outpath


def main(prog, args: list[str]):
    desc = "rotate images to correct orientation"
    ap = argparse.ArgumentParser(prog=prog, description=desc)
    ap.add_argument(
        "-w",
        "--overwrite",
        action="store_true",
        help="overwrite existing images",
    )
    ap.add_argument(
        "files",
        nargs="*",
        help="paths to images",
    )

    ns = ap.parse_args(args)
    for path in args:
        rotate_image(path, overwrite=ns.overwrite)


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
