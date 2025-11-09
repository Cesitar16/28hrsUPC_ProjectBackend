from __future__ import annotations

import time
from fastapi import APIRouter, Request

router = APIRouter(tags=["Health"], prefix="/health")


@router.get("", summary="Health check")
async def health_check(request: Request) -> dict[str, float | str]:
    start_time = getattr(request.app.state, "start_time", time.time())
    uptime = time.time() - start_time
    return {"status": "ok", "uptime_sec": round(uptime, 2)}
