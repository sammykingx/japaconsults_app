import redis


def redis_factory():
    redis_client = redis.StrictRedis(
        host="localhost",
        port=6379,
        db=0,
        encoding="utf-8",
        decode_responses=True,
        max_connections=100,
    )

    return redis_client
