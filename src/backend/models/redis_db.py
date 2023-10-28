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

    # check if key revoke_tokens exist
    if not redis_client.exists("revoked_tokens"):
        redis_client.lpush("revoked_tokens", "all revoked tokens")

    return redis_client
