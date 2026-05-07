from app.services.inflation_calculator import calculate_percent_change


def test_calculate_percent_change():
    assert calculate_percent_change(100, 110) == 10
