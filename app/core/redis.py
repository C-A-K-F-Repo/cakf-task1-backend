from redis.asyncio import ConnectionPool, Redis
from app.core.config import settings 

_pool: ConnectionPool | None = None
_client: Redis | None = None


async def get_redis_client() -> Redis:
    global _pool, _client
    if _client is not None:
        return _client
    

    if settings.REDIS_PASSWORD:
        redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
    else:
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

    _pool = ConnectionPool.from_url(
        redis_url,
        max_connections=10,
        decode_responses=True,
    )
    _client = Redis(connection_pool=_pool)
    return _client


async def close_redis_client() -> None:
    global _pool, _client
    if _client is not None:
        await _client.aclose()
        _client = None
    if _pool is not None:
        await _pool.aclose()
        _pool = None