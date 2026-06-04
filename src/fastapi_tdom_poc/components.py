from string.templatelib import Template
from typing import Annotated

from fastapi import FastAPI, Request

from .tdomhelpers import TDepends, IUrlFor


def Footer(
    app: Annotated[FastAPI, TDepends()],
    url_for: Annotated[IUrlFor, TDepends()],
    request: Annotated[Request, TDepends()],
) -> Template:
    assert app and url_for and request, "Testing DI."
    about_url = url_for("about")
    return t'<div class="footer"><a href={about_url}>About</a></div>'


def Layout(
    children: Template,
    head_t: Template | None = None,
) -> Template:
    return t"""<!doctype html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        {head_t}
    </head>
    {children}
</html>"""


def HeadAssets() -> Template:
    return t"""
    <link rel="stylesheet" href="https://ka-f.webawesome.com/webawesome@3.7.0/styles/webawesome.css">
    <script type="module" src="https://ka-f.webawesome.com/webawesome@3.7.0/webawesome.loader.js"></script>
"""
