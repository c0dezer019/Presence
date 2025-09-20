# Standard modules
import os

# Third party modules
from dotenv import load_dotenv
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

load_dotenv()

R_HOST = os.getenv("REDIS_HOST", "localhost")
R_PORT = os.getenv("REDIS_PORT", 6379)


def create_redis_connection():
    try:
        r = Redis(
            host=R_HOST,
            port=R_PORT,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )

        r.ping()

        return r
    except RedisConnectionError:
        raise
    except Exception:
        raise
