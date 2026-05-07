def calculate_percent_change(previous: float, current: float) -> float:
    if previous == 0:
        raise ValueError("previous value must not be zero")
    return round(((current - previous) / previous) * 100, 2)
