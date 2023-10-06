import phonenumbers


def verify_phone_num(number: str) -> bool:
    """verify's the number (a string object) if its a possible phumber or not"""

    phone_num = phonenumbers.parse(number)
    try:
        valid_num = phonenumbers.is_valid_number(phone_num)

    except Exception as err:
        return None

    return valid_num
