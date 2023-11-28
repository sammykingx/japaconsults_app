verify_card_charge = {
    #    200: {
    #        "description": "successfull card payments",
    #        "content": {
    #            "application/json": {
    #                "example": {
    #                    "transactionComplete": True,
    #                    "ref_id": "REF-1699625474",
    #                    "inv_id": "JPC-1699579688",
    #                    "amount": 750.12,
    #                    "chargedamount": 750.12,
    #                    "currency": "NGN",
    #                },
    #            },
    #        },
    #    },
    #
    400: {
        "content": {
            "application/json": {
                "example": {
                    "detail": "CARD DECLINED",
                },
            },
        },
    },
}
