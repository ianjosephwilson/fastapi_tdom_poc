from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from inspect import isclass
from string.templatelib import Template
from typing import (
    Any,
    get_origin,
    get_args,
    Annotated,
    get_type_hints,
    is_protocol,
    Protocol,
    runtime_checkable,
)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette_tdom import TdomTemplates as _TdomTemplates, TdomCtx
from tdom.processor import (
    TemplateProcessor,
    ProcessContext,
    Attribute,
    IComponentProcessor,
    ComponentProcessor,
)
from tdom.scope import ScopedTemplate
from tdom.tnodes import TAttribute


def TdomTemplates():
    return _TdomTemplates(to_html=to_html) # Load in configured processor


@dataclass(frozen=True, slots=True)
class TDepends[T]:
    """
    Wrapper around template dependency.
    """

    dependency: T | None = None
    "Dependency type to inject, if None then use first value of `Annotated`."


@dataclass(frozen=True)
class FastAPIComponentProcessor(IComponentProcessor):
    """
    Component processor that tries to inject a fixed set of fastapi
    dependencies if request with `TDepends` before calling the default
    component process.
    """

    default_component_processor: IComponentProcessor = field(
        default_factory=ComponentProcessor
    )

    @lru_cache(128)
    def _get_deps(self, component_callable: Callable) -> tuple[tuple[str, type], ...]:
        deps = []
        for arg, hint in get_type_hints(
            component_callable, include_extras=True
        ).items():
            origin = get_origin(hint)
            if origin is Annotated:
                a_args = get_args(hint)
                for a_arg in a_args[1:]:
                    if isinstance(a_arg, TDepends):
                        a_type = (
                            a_arg.dependency
                            if a_arg.dependency is not None
                            else a_args[0]
                        )
                        if a_type is not None:
                            deps.append((arg, a_type))
                        else:
                            raise TypeError("Cannot resolve dependency for `None`.")
        return tuple(deps)

    def _get_request(self) -> Request:
        value = TdomCtx.get()
        if value.request is None:
            raise TypeError("Request is not set!")
        else:
            return value.request

    def process(
        self,
        template: Template,
        last_ctx: ProcessContext,
        component_callable: object,
        attrs: tuple[TAttribute, ...],
        component_template: Template,
        provided_attrs: tuple[Attribute, ...] = (),
    ) -> Template | ScopedTemplate:
        deps = (
            self._get_deps(component_callable) if callable(component_callable) else ()
        )
        if deps:
            ext_attrs = []
            for arg, dep in deps:
                if isclass(dep) and issubclass(dep, Request):
                    request = self._get_request()
                    ext_attrs.append((arg, request))
                elif isclass(dep) and issubclass(dep, FastAPI):  # The app itself.
                    request = self._get_request()
                    ext_attrs.append((arg, request.app))
                elif is_protocol(dep) and issubclass(dep, IUrlFor):
                    request = self._get_request()
                    ext_attrs.append((arg, request.url_for))
                else:
                    raise ValueError(
                        f"Unknown request for dependency named {arg} of type {dep}"
                    )
            extended_attrs = tuple(ext_attrs)
        else:
            extended_attrs = ()
        return self.default_component_processor.process(
            template=template,
            last_ctx=last_ctx,
            component_callable=component_callable,
            attrs=attrs,
            component_template=component_template,
            provided_attrs=extended_attrs + provided_attrs,
        )


_default_template_processor = TemplateProcessor(
    component_processor_api=FastAPIComponentProcessor()
)
"Add fastapi DI to TDOM components."


_default_process_ctx = ProcessContext()


def to_html(template: Template, assume_ctx: ProcessContext | None = None) -> str:
    if assume_ctx is None:
        assume_ctx = _default_process_ctx
    return _default_template_processor.process(template, assume_ctx)


@runtime_checkable
class IUrlFor(Protocol):
    def __call__(self, name: str, **kargs: Any) -> str: ...
