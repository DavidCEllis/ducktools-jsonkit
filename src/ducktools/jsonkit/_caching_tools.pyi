"""
This type stub file was generated by pyright.
"""
from ducktools.lazyimporter import LazyImporter, ModuleImport
from functools import lru_cache

from collections.abc import Callable
from typing import Any

_laz: LazyImporter = ...

@lru_cache
def field_default(fieldnames: tuple[str, ...]) -> Callable[[Any], Any]: ...
def make_dataclass_default(exclude_fields: tuple[str, ...]) -> Callable[[Any], Any]: ...
def dataclass_default(o: Any) -> Any: ...
