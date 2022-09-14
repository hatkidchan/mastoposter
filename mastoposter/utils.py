from html import escape
from bs4.element import Tag, PageElement


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


def node_to_html(el: PageElement) -> str:
    if isinstance(el, Tag):
        if el.name == "a":
            return '<a href="{}">{}</a>'.format(
                escape(el.attrs["href"]),
                str.join("", map(node_to_html, el.children)),
            )
        elif el.name == "p":
            return str.join("", map(node_to_html, el.children)) + "\n\n"
        elif el.name == "br":
            return "\n"
        return str.join("", map(node_to_html, el.children))
    return escape(str(el))


def node_to_markdown(el: PageElement) -> str:
    if isinstance(el, Tag):
        if el.name == "a":
            return "[%s](%s)" % (
                md_escape(str.join("", map(node_to_markdown, el.children))),
                el.attrs["href"],
            )
        elif el.name == "p":
            return str.join("", map(node_to_markdown, el.children)) + "\n\n"
        elif el.name == "br":
            return "\n"
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
        return str.join("", map(node_to_plaintext, el.children))
    return str(el)
