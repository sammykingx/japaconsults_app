# email token response

response_codes = {
        404: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No user account found",
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
