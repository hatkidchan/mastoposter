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
from configparser import ConfigParser
from html import escape
from logging import getLogger
from typing import Callable, Dict
from bs4.element import Tag, PageElement

logger = getLogger("utils")


def md_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("*", "\\*")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("_", "\\_")
        .replace("~", "\\~")
        .replace("|", "\\|")
        .replace("`", "\\`")
    )


def normalize_config(conf: ConfigParser):
    for section in conf.sections():
        _remove = set()
        for k, v in conf[section].items():
            normalized_key = k.replace(" ", "_").replace("-", "_")
            if k == normalized_key:
                continue
            logger.info(
                "moving %r.%r -> %r.%r", section, k, section, normalized_key
            )
            conf[section][normalized_key] = v
            _remove.add(k)
        for k in _remove:
            logger.info("removing key %r.%r", section, k)
            del conf[section][k]


def node_to_html(el: PageElement) -> str:
    TAG_TRANSFORMS: Dict[
        str,
        Callable[
            [
                Tag,
            ],
            str,
        ],
    ] = {
        "a": lambda tag: '<a href="{}">{}</a>'.format(
            escape(tag.attrs["href"]),
            str.join("", map(node_to_html, tag.children)),
        ),
        "p": lambda tag: (
            str.join("", map(node_to_html, tag.children)) + "\n\n"
        ),
        "i": lambda tag: (
            "<i>%s</i>" % str.join("", map(node_to_html, tag.children))
        ),
        "b": lambda tag: (
            "<b>%s</b>" % str.join("", map(node_to_html, tag.children))
        ),
        "s": lambda tag: (
            "<s>%s</s>" % str.join("", map(node_to_html, tag.children))
        ),
        "u": lambda tag: (
            "<u>%s</u>" % str.join("", map(node_to_html, tag.children))
        ),
        "pre": lambda tag: (
            "\n<pre>%s</pre>\n" % str.join("", map(node_to_html, tag.children))
        ),
        "code": lambda tag: (
            "<code>%s</code>" % str.join("", map(node_to_html, tag.children))
        ),
        "blockquote": lambda tag: "\n%s"
        % str.join(
            "\n",
            (
                "| %s" % part
                for part in str.join(
                    "", map(node_to_html, tag.children)
                ).split("\n")
            ),
        ),
        "br": lambda _: "\n",
        # NOTE may fail on nested lists
        "ul": lambda tag: (
            "\n"
            + str.join(
                "\n",
                (
                    " \u2022 "
                    + node_to_html(li).replace("\n", "\n   ").rstrip()
                    for li in tag.children
                ),
            )
            + "\n"
        ),
        "ol": lambda tag: (
            "\n"
            + str.join(
                "\n",
                (
                    "%d. %s"
                    % (i, node_to_html(li).replace("\n", "\n   ").rstrip())
                    for i, li in enumerate(tag.children, 1)
                ),
            )
            + "\n"
        ),
    }

    TAG_SUBSTITUTIONS: Dict[str, str] = {
        "strong": "b",
        "em": "i",
        "del": "s",
        "ins": "u",
    }

    if isinstance(el, Tag):
        if el.name in TAG_TRANSFORMS:
            return TAG_TRANSFORMS[el.name](el)
        if el.name in TAG_SUBSTITUTIONS:
            sub = TAG_SUBSTITUTIONS[el.name]
            if sub in TAG_TRANSFORMS:
                return TAG_TRANSFORMS[sub](el)
        return str.join("", map(node_to_html, el.children))
    return escape(str(el))


def node_to_markdown(el: PageElement) -> str:
    TAG_TRANSFORMS: Dict[
        str,
        Callable[
            [
                Tag,
            ],
            str,
        ],
    ] = {
        "a": lambda tag: "[{}]({})".format(
            md_escape(str.join("", map(node_to_markdown, tag.children))),
            tag.attrs["href"],
        ),
        "p": lambda tag: (
            str.join("", map(node_to_markdown, tag.children)) + "\n\n"
        ),
        "i": lambda tag: (
            "_%s_" % str.join("", map(node_to_markdown, tag.children))
        ),
        "b": lambda tag: (
            "*%s*" % str.join("", map(node_to_markdown, tag.children))
        ),
        "s": lambda tag: (
            "~%s~" % str.join("", map(node_to_markdown, tag.children))
        ),
        "u": lambda tag: (
            "__%s__" % str.join("", map(node_to_markdown, tag.children))
        ),
        "pre": lambda tag: (
            "\n``%s``\n" % str.join("", map(node_to_markdown, tag.children))
        ),
        "code": lambda tag: (
            "`%s`" % str.join("", map(node_to_markdown, tag.children))
        ),
        "blockquote": lambda tag: (
            "\n%s"
            % str.join(
                "\n",
                (
                    "▍%s" % part
                    for part in str.join(
                        "", map(node_to_markdown, tag.children)
                    ).split("\n")
                ),
            )
        ),
        "br": lambda _: "\n",
        # NOTE may fail on nested lists
        "ul": lambda tag: (
            "\n%s\n"
            % str.join(
                "\n",
                (
                    " \u2022 "
                    + node_to_markdown(li).replace("\n", "\n   ").rstrip()
                    for li in tag.children
                ),
            )
        ),
        "ol": lambda tag: (
            "\n%s\n"
            % str.join(
                "\n",
                (
                    "%d. %s"
                    % (i, node_to_markdown(li).replace("\n", "\n   ").rstrip())
                    for i, li in enumerate(tag.children, 1)
                ),
            )
        ),
    }

    TAG_SUBSTITUTIONS: Dict[str, str] = {
        "strong": "b",
        "em": "i",
        "del": "s",
        "ins": "u",
    }

    if isinstance(el, Tag):
        if el.name in TAG_TRANSFORMS:
            return TAG_TRANSFORMS[el.name](el)
        if el.name in TAG_SUBSTITUTIONS:
            sub = TAG_SUBSTITUTIONS[el.name]
            if sub in TAG_TRANSFORMS:
                return TAG_TRANSFORMS[sub](el)
        return str.join("", map(node_to_markdown, el.children))
    return md_escape(str(el))


def node_to_plaintext(el: PageElement) -> str:
    if isinstance(el, Tag):
        if el.name == "a":
            return "%s (%s)" % (
                str.join("", map(node_to_plaintext, el.children)),
                el.attrs["href"],
            )
        elif el.name == "p":
            return str.join("", map(node_to_plaintext, el.children)) + "\n\n"
        elif el.name == "br":
            return "\n"
        elif el.name in ("ol", "ul"):
            children = map(node_to_plaintext, el.children)
            return "\n%s\n" % str.join(
                "\n",
                (
                    " \u2022 %s" % li.replace("\n", "\n   ").strip()
                    for li in children
                )
                if el.name == "ol"
                else (
                    "%d. %s" % (i, li.replace("\n", "\n   ").strip())
                    for i, li in enumerate(children)
                ),
            )
        return str.join("", map(node_to_plaintext, el.children))
    return str(el)
