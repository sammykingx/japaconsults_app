# Documents upload

upload_response_codes = {
        400: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "filename greater than 45 characters",
                    },
                },
            },
        },

        404: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid folder",
                    },

                },
            },
        },

        413: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "file too large",
                    },
                },
            },
        },

        415: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unsupported file format",
                    },
                },
            },
        },

        500: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "encountered some issues while processing request",
                    },
                },
            },
        },
}
