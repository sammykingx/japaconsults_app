from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pwd(raw_pwd: str) -> str:
    """returns a hashed version of the plain_pwd"""

    return pwd_context.hash(raw_pwd)


def verify_pwd(raw_pwd: str, hashed_pwd: str) -> bool:
    """checks if raw_pwd and hashed_pwd are same"""

    return pwd_context.verify(raw_pwd, hashed_pwd)
