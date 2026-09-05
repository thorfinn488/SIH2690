import pytest
from app.ai_mocks.mock_ai_services import calculate_price


def test_calculate_price_low_complexity():
    res = calculate_price(material_cost=200.0, days_to_make=2, complexity="low")
    assert "suggested_price" in res
    assert "price_range" in res
    assert len(res["price_range"]) == 2
    # Base: 200 + (2*400) + 0 = 1000 -> suggested = round(1250, -1) = 1250
    assert res["suggested_price"] == 1250.0
    assert res["price_range"][0] < res["suggested_price"] < res["price_range"][1]


def test_calculate_price_medium_complexity():
    res = calculate_price(material_cost=500.0, days_to_make=3, complexity="medium")
    # Base: 500 + (3*400) + 200 = 1900 -> suggested = round(2375, -1) = 2380
    assert res["suggested_price"] == 2380.0
    assert res["price_range"][0] == 2140.0


def test_calculate_price_high_complexity():
    res = calculate_price(material_cost=1000.0, days_to_make=5, complexity="high")
    # Base: 1000 + (5*400) + 500 = 3500 -> suggested = round(4375, -1) = 4380
    assert res["suggested_price"] == 4380.0
    assert res["price_range"][0] < res["suggested_price"] < res["price_range"][1]


def test_calculate_price_deterministic():
    res1 = calculate_price(material_cost=650.0, days_to_make=4, complexity="high")
    res2 = calculate_price(material_cost=650.0, days_to_make=4, complexity="high")
    assert res1 == res2
