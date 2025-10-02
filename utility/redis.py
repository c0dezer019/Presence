# Standard modules
import os
from typing import Optional

# Third party modules
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

R_HOST = os.getenv("REDIS_HOST", "localhost")
R_PORT = os.getenv("REDIS_PORT", 6379)


class AsyncRedisManager:
    host = os.getenv("REDIS_HOST", "localhost")
    __port_raw = os.getenv("REDIS_PORT")

    try:
        port = int(__port_raw) if __port_raw is not None and __port_raw != "" else 6379
    except ValueError:
        port = 6379

    def __init__(
        self,
        host: Optional[int] = host,
        port: Optional[int] = port,
        db=0,
        max_connections=20,
    ):
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            max_connections=max_connections,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            decode_responses=True,
        )

        self.client = redis.Redis(connection_pool=self.pool)

    async def close(self):
        await self.client.aclose()
        await self.pool.aclose()

    def get_p_info(self) -> int:
        return self.pool.max_connections
