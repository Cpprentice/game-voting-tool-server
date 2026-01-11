from typing import Any, Protocol

from starlette.datastructures import URL


class UrlFactory(Protocol):
    def url_for(self, name: str, /, **path_params: Any) -> URL:
        ...
