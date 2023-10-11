from fastapi import HTTPException, status
import phonenumbers


def verify_phone_num(number: str) -> bool:
    """verify's the number (a string object) if its a possible phumber or not"""

    try:
        phone_num = phonenumbers.parse(number)
        valid_num = phonenumbers.is_valid_number(phone_num)

    except phonenumbers.phonenumberutil.NumberParseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format",
        )

    except Exception as err:
        return None

    return valid_num
