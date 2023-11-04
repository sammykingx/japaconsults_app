# Verify email token response

response_codes = {
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "msg": "User account verified",
                        "name": "John Doe",
                        "email": "useremail@gmail.com",
                        "is_verified": True,
                    },
                },
            },
        },

        400: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid/expired verification token",
                    },
                },
            },
        },
        
        409: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User already verified",
                    }
                }
            }
        },

        500: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "encountered some issues while processing request",
                    }
                }
            }
        }
}
