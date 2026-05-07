from app.services.price_normalizer import calculate_price_per_unit


def test_calculate_price_per_unit():
    assert calculate_price_per_unit(280, 25) == 11.2
