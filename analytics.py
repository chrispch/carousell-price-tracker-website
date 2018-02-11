
def price_statistics(data):
    price_stat = {}
    total_price = 0
    price_list = []
    for d in data:
        total_price += d.price
        price_list.append(d.price)
    price_stat["ave_price"] = total_price/len(data)
    price_stat["max_price"] = max(price_list)
    price_stat["min_price"] = min(price_list)
    return price_stat

