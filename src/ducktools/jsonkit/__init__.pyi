"""
Type stubs to avoid importing typing.
"""
from typing import TYPE_CHECKING, Any, TypeVar
import types

from ducktools.lazyimporter import LazyImporter, MultiFromImport, get_module_funcs
from collections.abc import Callable

if TYPE_CHECKING:
    from ._caching_tools import (
        field_default,
        dataclass_default,
        make_dataclass_default,
    )

__version__: str = ...
__all__: list[str] = [
    "merge_defaults",
    "field_default",
    "method_default",
    "dataclass_default",
    "make_dataclass_default",
    "JSONRegister",
]
_laz: LazyImporter = ...

def merge_defaults(*defaults: Callable[[Any], Any]) -> Callable[[Any], Any]: ...
def method_default(method_name: str) -> Callable[[Any], Any]: ...

class _RegisterDecorator:
    func: Callable[[Any], Any]
    registry: JSONRegister

    def __init__(self, func: Callable[[Any], Any], registry: JSONRegister) -> None: ...
    def __set_name__(self, owner: type, name: str) -> None: ...

_FuncT = TypeVar("_FuncT", bound=Callable[[Any], Any])

class JSONRegister:
    registry: list[tuple[type, Callable[[Any], Any]]]

    def __init__(self) -> None: ...
    def register(self, cls: type, func: Callable[[Any], Any]) -> None: ...
    def register_function(self, cls: type) -> Callable[[_FuncT], _FuncT]: ...

    def register_method(self, method: types.MethodType) -> _RegisterDecorator: ...
    def default(self, o: Any) -> Any: ...
