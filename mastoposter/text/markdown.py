from mastoposter.text import (
    nodes_process,
    register_converter,
    register_fmt_converter,
    node_process,
)

from typing import Optional
from bs4.element import Tag
from html import escape


@register_converter("a", "markdown")
def proc_tag_a_to_markdown(tag: Tag):
    return "[%s](%s)" % (
        nodes_process(tag.children, "markdown"),
        escape(tag.attrs.get("href", "#")),
    )


register_fmt_converter("%s\n\n", "p", "markdown")
register_fmt_converter("*%s*", "i", "markdown")
register_fmt_converter("*%s*", "em", "markdown")
register_fmt_converter("**%s**", "b", "markdown")
register_fmt_converter("**%s**", "strong", "markdown")
register_fmt_converter("~~%s~~", "s", "markdown")
register_fmt_converter("~~%s~~", "del", "markdown")
register_fmt_converter("__%s__", "u", "markdown")
register_fmt_converter("__%s__", "ins", "markdown")
register_fmt_converter("\n", "br", "markdown")
register_fmt_converter("\n```%s```\n", "pre", "markdown")
register_fmt_converter("`%s`", "code", "markdown")


@register_converter("span", "markdown")
def proc_tag_span_to_markdown(tag: Tag) -> Optional[str]:
    if "_mfm_blur_" in tag.attrs.get("class", ""):
        return "||%s||" % nodes_process(tag.children, "markdown")
    return None


@register_converter("blockquote", "markdown")
def proc_tag_blockquote_to_markdown(tag: Tag) -> str:
    return str.join(
        "\n",
        (
            "> " + line
            for line in nodes_process(tag.children, "markdown")
            .strip()
            .split("\n")
        ),
    )


@register_converter("ul", "markdown")
def proc_tag_ul_to_markdown(tag: Tag) -> str:
    return "\n" + str.join(
        "\n",
        (
            "* " + node_process(el, "markdown").replace("\n", "\n   ").rstrip()
            for el in tag.children
        ),
    )


@register_converter("li", "markdown")
def proc_tag_li_to_markdown(tag: Tag) -> str:
    return "\n" + str.join(
        "\n",
        (
            "%d. %s"
            % (i, node_process(el, "markdown").replace("\n", "\n   ").rstrip())
            for i, el in enumerate(tag.children, 1)
        ),
    )
