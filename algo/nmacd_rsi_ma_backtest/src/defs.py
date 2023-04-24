"""
definitions
"""


class BROKER:
    PRICE_DIGITS = {
        "EUR_USD": 5,
        "USD_JPY": 3,
        "XAU_USD": 3,
    }

    POSITION_UNIT = {
        "EUR_USD": 1,
        "USD_JPY": 1,
        "XAU_USD": 1,
    }

    SPREAD = {
        "EUR_USD": 0.00015,
    }

    COMMISSION = {
        "EUR_USD": 0.000075,
    }

    LEVERAGE = {
        "EUR_USD": 50,
    }
