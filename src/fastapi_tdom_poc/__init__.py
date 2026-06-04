from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from inspect import isclass
from string.templatelib import Template

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from .tdomhelpers import TdomTemplates
from .components import Layout, HeadAssets, Footer


app = FastAPI()


tdom_templates = TdomTemplates()


def make_home_page(head_t: Template) -> Template:
    return t"""
<{Layout} head_t={head_t}>
    <h1>Hello, Fast API!!</h1>
    <{Footer} />
</{Layout}>
"""


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    page_t = make_home_page(head_t=t'<{HeadAssets} />')
    return tdom_templates.TemplateResponse(request, page_t)


def make_about_page(head_t: Template) -> Template:
    page_t = t"""
<{Layout} head_t={head_t}>
    <h1>About</h1>
</{Layout}>
"""
    return page_t


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    head_t = t"<title>Home</title>"
    page_t = make_about_page(head_t=head_t)
    return tdom_templates.TemplateResponse(request, page_t)
