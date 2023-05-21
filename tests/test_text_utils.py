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

from bs4 import BeautifulSoup
from pytest import mark

from mastoposter.text import md_escape, node_process


def test_md_escape():
    assert md_escape(r"text") == r"text"
    assert md_escape(r"*meow*") == r"\*meow\*"
    assert md_escape(r"\~test") == r"\\\~test"


def test_node_to_plaintext_strip_tag():
    soup = BeautifulSoup('<b>test</b>', features="lxml")
    assert node_process(soup, "plain") == "test"


def test_node_to_plaintext_tag_a():
    soup = BeautifulSoup('<a href="https://example.com">test</a>',
                         features="lxml")
    assert node_process(soup, "plain") == "test (https://example.com)"


def test_node_to_plaintext_tag_p():
    soup = BeautifulSoup('<p>Lorem ipsum</p>', features="lxml")
    assert node_process(soup, "plain") == "Lorem ipsum\n\n"


def test_node_to_plaintext_tag_br():
    soup = BeautifulSoup('<p>test1<br>test2</p>', features="lxml")
    assert node_process(soup, "plain").rstrip() == "test1\ntest2"


def test_node_to_plaintext_tag_blockquote():
    soup = BeautifulSoup('<blockquote>Lorem ipsum</blockquote>',
                         features="lxml")
    assert node_process(soup, "plain").rstrip() == "\u258d Lorem ipsum"


def test_node_to_plaintext_tag_ul():
    soup = BeautifulSoup('<ul><li>test1<li>test2</ul>', features="lxml")
    assert node_process(soup, "plain") == "\n\u2022 test1\n\u2022 test2"


def test_node_to_plaintext_tag_ol():
    soup = BeautifulSoup('<ol><li>test1<li>test2</ol>', features="lxml")
    assert node_process(soup, "plain") == "\n1. test1\n2. test2"


@mark.parametrize("tag", ["video", "span"])
def test_node_to_markdown_strip_tag(tag):
    soup = BeautifulSoup('<{0}>test</{0}>'.format(tag), features="lxml")
    assert node_process(soup, "markdown") == "test"


def test_node_to_markdown_tag_a():
    soup = BeautifulSoup('<a href="https://example.com">test</a>',
                         features="lxml")
    assert node_process(soup, "markdown") == "[test](https://example.com)"


def test_node_to_markdown_tag_p():
    soup = BeautifulSoup('<p>Lorem ipsum</p>', features="lxml")
    assert node_process(soup, "markdown") == "Lorem ipsum\n\n"


def test_node_to_markdown_tag_i():
    soup = BeautifulSoup('<i>test</i>', features="lxml")
    assert node_process(soup, "markdown") == "*test*"


def test_node_to_markdown_tag_b():
    soup = BeautifulSoup('<b>test</b>', features="lxml")
    assert node_process(soup, "markdown") == "**test**"


def test_node_to_markdown_tag_s():
    soup = BeautifulSoup('<s>test</s>', features="lxml")
    assert node_process(soup, "markdown") == "~~test~~"


def test_node_to_markdown_tag_u():
    soup = BeautifulSoup('<u>test</u>', features="lxml")
    assert node_process(soup, "markdown") == "__test__"


def test_node_to_markdown_tag_pre():
    soup = BeautifulSoup('<pre>Lorem ipsum</pre>', features="lxml")
    assert node_process(soup, "markdown") == "\n```Lorem ipsum```\n"


def test_node_to_markdown_tag_code():
    soup = BeautifulSoup('<code>test</code>', features="lxml")
    assert node_process(soup, "markdown") == "`test`"


def test_node_to_markdown_tag_blockquote():
    soup = BeautifulSoup('<blockquote>Lorem ipsum</blockquote>', features="lxml")
    assert node_process(soup, "markdown") == "> Lorem ipsum"


def test_node_to_markdown_tag_br():
    soup = BeautifulSoup('<p>test1<br>test2</p>', features="lxml")
    assert node_process(soup, "markdown").rstrip() == "test1\ntest2"


def test_node_to_markdown_tag_ul():
    soup = BeautifulSoup('<ul><li>test1<li>test2</ul>', features="lxml")
    assert node_process(soup, "markdown") == "\n* test1\n* test2"


def test_node_to_markdown_tag_ol():
    soup = BeautifulSoup('<ol><li>test1<li>test2</ol>', features="lxml")
    assert node_process(soup, "markdown") == "\n1. test1\n2. test2"


@mark.parametrize("tag", ["video", "span"])
def test_node_to_html_strip_tag(tag):
    soup = BeautifulSoup('<{0}>test</{0}>'.format(tag), features="lxml")
    assert node_process(soup, "html") == "test"


@mark.parametrize("tag", ["i", "b", "s", "u", "code"])
def test_node_to_html_keep_tag(tag):
    html = '<{0}>test</{0}>'.format(tag)
    soup = BeautifulSoup(html, features="lxml")
    assert node_process(soup, "html") == html


@mark.parametrize("old_tag,new_tag",
                  [("strong", "b"), ("em", "i"), ("del", "s"), ("ins", "u")])
def test_node_to_html_subst_tag(old_tag, new_tag):
    soup = BeautifulSoup('<{0}>test</{0}>'.format(old_tag), features="lxml")
    assert node_process(soup, "html") == '<{0}>test</{0}>'.format(new_tag)


def test_node_to_html_tag_a():
    html = '<a href="https://example.com">test</a>'
    soup = BeautifulSoup(html, features="lxml")
    assert node_process(soup, "html") == html


def test_node_to_html_tag_p():
    soup = BeautifulSoup('<p>Lorem ipsum</p>', features="lxml")
    assert node_process(soup, "html") == "Lorem ipsum\n\n"


def test_node_to_html_tag_pre():
    soup = BeautifulSoup('<pre>Lorem ipsum</pre>', features="lxml")
    assert node_process(soup, "html") == "\n<pre>Lorem ipsum</pre>\n"


def test_node_to_html_tag_blockquote():
    soup = BeautifulSoup('<blockquote>Lorem ipsum</blockquote>',
                         features="lxml")
    assert node_process(soup, "html").rstrip() == "▍ Lorem ipsum"


def test_node_to_html_tag_br():
    soup = BeautifulSoup('<p>test1<br>test2</p>', features="lxml")
    assert node_process(soup, "html").rstrip() == "test1\ntest2"


def test_node_to_html_tag_ul():
    soup = BeautifulSoup('<ul><li>test1<li>test2</ul>', features="lxml")
    assert node_process(soup, "html") == "\n\u2022 test1\n\u2022 test2"


def test_node_to_html_tag_ol():
    soup = BeautifulSoup('<ol><li>test1<li>test2</ol>', features="lxml")
    assert node_process(soup, "html") == "\n1. test1\n2. test2"


def test_node_to_html_spoiler():
    soup = BeautifulSoup('<span class="_mfm_blur_">test</span>', features="lxml")
    assert node_process(soup, "html") == '<span class="tg-spoiler">test</span>'
