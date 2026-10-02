from trading_engine.structures.ratios import classify_ratio


def test_ratio_one_is_approximate():
    assert classify_ratio(0.95) == "1"
    assert classify_ratio(1.10) == "1"


def test_ratio_two_is_approximate():
    assert classify_ratio(1.90) == "2"
    assert classify_ratio(2.20) == "2"
