from dataclasses import dataclass
from string.templatelib import Template
from typing import Annotated

from .tdomhelpers import TDepends, IUrlFor


@dataclass
class Footer:
    """
    Component class to manage footer.

    We break this out into a class so we can use helper methods.
    """

    url_for: Annotated[IUrlFor, TDepends()]

    def _get_links(self) -> list[tuple[str, str]]:
        return [
            (self.url_for("home"), "Home"),
            (self.url_for("about"), "About"),
        ]

    def _get_els(self) -> list[Template]:
        # Insert a separate between links.
        footer_els = []
        SEP = t" | "
        links = self._get_links()
        for index, (href, content) in enumerate(links):
            if index != 0:
                footer_els.append(SEP)
            footer_els.append(t"<a href={href}>{content}</a>")
        return footer_els

    def __call__(self) -> Template:
        footer_els = self._get_els()
        return t'<div class="footer">{footer_els}</div>'


def Layout(
    children: Template,
    head_t: Template | None = None,
) -> Template:
    return t"""<!doctype html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        <{HeadAssets} />
        {head_t}
    </head>
    {children}
</html>"""


def HeadAssets() -> Template:
    return t"""
    <link rel="stylesheet" href="https://ka-f.webawesome.com/webawesome@3.7.0/styles/webawesome.css">
    <script type="module" src="https://ka-f.webawesome.com/webawesome@3.7.0/webawesome.loader.js"></script>
"""
