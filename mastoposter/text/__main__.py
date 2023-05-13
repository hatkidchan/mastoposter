"""
mastoposter - configurable reposter from Mastodon-compatible Fediverse servers
Copyright (C) 2022-2023 hatkidchan <hatkidchan@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

from mastoposter.text import node_process, VALID_OUTPUT_TYPES
from argparse import ArgumentParser, FileType
from typing import get_args as T_get_args
from bs4 import BeautifulSoup
import sys

parser = ArgumentParser("mastoposter.text", description="HTML-to-* converter")

parser.add_argument(
    "--type",
    "-t",
    choices=T_get_args(VALID_OUTPUT_TYPES),
    default=T_get_args(VALID_OUTPUT_TYPES)[0],
    dest="output_type",
)
parser.add_argument("file", default=sys.stdin, type=FileType("r"))

args = parser.parse_args()

soup = BeautifulSoup(args.file.read(), "lxml")
print(node_process(soup, args.output_type))
