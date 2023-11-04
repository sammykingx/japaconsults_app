# change user password response

response_codes = {
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "msg": "Successful",
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
