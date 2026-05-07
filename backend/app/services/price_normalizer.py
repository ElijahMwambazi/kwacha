def calculate_price_per_unit(price: float, quantity: float) -> float:
    if quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    return round(price / quantity, 4)
