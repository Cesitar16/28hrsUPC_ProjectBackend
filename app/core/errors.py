from __future__ import annotations

from typing import Any, NoReturn, Optional

from fastapi import HTTPException


def http_error(
    status_code: int,
    code: str,
    message: str,
    *,
    details: Optional[Any] = None,
    hint: Optional[str] = None,
) -> HTTPException:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    if hint:
        payload["error"]["hint"] = hint
    return HTTPException(status_code=status_code, detail=payload)


def raise_http_error(*args, **kwargs) -> NoReturn:
    raise http_error(*args, **kwargs)
