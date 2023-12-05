# This module containss code for saving the user email token
# format email:email_token

from models import redis_db


redis = redis_db.redis_factory()


def add_email_token(key, token: str, expires_in=3600):
    """add's the users email token to redis and then sets the expiration time

    key: the key to be stored
    token: the value of the key
    expires_in: the expiration time in seconds
    """

    # key = user_email + ":email_token"
    # if not redis.exists(key):
    #    redis.set(key, token)

    redis.set(key, token)
    redis.expire(key, expires_in)
