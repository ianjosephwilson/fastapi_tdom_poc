from string.templatelib import Template

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from .tdomhelpers import TdomTemplates
from .components import Layout, Footer


app = FastAPI()


tdom_templates = TdomTemplates()


def make_home_page() -> Template:
    head_t = t"""
<title>Home</title>
"""
    return t"""
<{Layout} head_t={head_t}>
    <h1>Hello, Fast API!!</h1>
    <{Footer} />
</{Layout}>
"""


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    page_t = make_home_page()
    return tdom_templates.TemplateResponse(request, page_t)


def make_about_page() -> Template:
    head_t = t"<title>About</title>"
    page_t = t"""
<{Layout} head_t={head_t}>
    <h1>About</h1>

    <p>This project is a prototype.</p>
    <{Footer} />
</{Layout}>
"""
    return page_t


@app.get("/about", response_class=HTMLResponse)
def about(request: Request) -> HTMLResponse:
    page_t = make_about_page()
    return tdom_templates.TemplateResponse(request, page_t)
