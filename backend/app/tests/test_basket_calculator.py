from app.services.basket_calculator import calculate_basket_total


def test_calculate_basket_total():
    assert calculate_basket_total([10, 20.5]) == 30.5
