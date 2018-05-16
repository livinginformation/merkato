def getQueryParameters(type, ticker, amount, price):
    formatted_amount = "{:.8f}".format(amount)
    formatted_price = "{:.8f}".format(price)
    return {
        "method": type,
        "market": "BTC",
        "coin": ticker,
        "amount": formatted_amount,
        "price": formatted_price
    }


def translate_ticker(coin, base):
    if base == "BTC":
        if coin == "ZEC":
            return "BTC_ZEC"
        if coin == "PPC":
            return "BTC_PPC"
        if coin == "EMC":
            return "BTC_EMC"
        if coin == "ICN":
            return "BTC_ICN"
        if coin == "POT":
            return "BTC_POT"
        if coin == "NMC":
            return "BTC_NMC"
        if coin == "DOGE":
            return "BTC_DOGE"
        if coin == "BCY":
            return "BTC_BCY"
        if coin == "LTC":
            return "BTC_LTC"
        if coin == "DASH":
            return "BTC_DASH"
        if coin == "ETH":
            return "BTC_ETH"
        if coin == "BLK":
            return "BTC_BLK"
        if coin == "DTB":
            return "BTC_DTB"
        if coin == "DCR":
            return "BTC_DCR"
        if coin == "GNT":
            return "BTC_GNT"
        if coin == "PEPECASH":
            return "BTC_PEPECASH"
        if coin == "SYS":
            return "BTC_SYS"
        if coin == "XCP":
            return "BTC_XCP"
        if coin == "XMR":
            return "BTC_XMR"

    raise NotImplementedError("Unknown pair: coin={}, base={}".format(coin, base))
