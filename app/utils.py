import time
from fastapi import Request, HTTPException, status

USAGE_HISTORY = {}


async def rate_limit(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()

    window = 60
    limit = 10

    history = USAGE_HISTORY.get(client_ip, [])

    valid_history = [t for t in history if now - t < window]

    if len(valid_history) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests . Please wait a minute",
        )

    valid_history.append(now)
    USAGE_HISTORY[client_ip] = valid_history
