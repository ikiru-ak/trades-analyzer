import pytest
from project import normalize_header, normalize_side, parse_number, calculate_pnl, summarise


def test_normalize_header():
    assert normalize_header("date") == "date"
    assert normalize_header("Ticker") == "symbol"
    assert normalize_header("  QTY ") == "quantity"
    assert normalize_header("Entry Price") == "entry"
    assert normalize_header("Fees") is None


def test_normalize_side():
    assert normalize_side("buy") == "buy"
    assert normalize_side(" Long ") == "buy"
    assert normalize_side("B") == "buy"
    assert normalize_side("SOLD") == "sell"
    assert normalize_side("short") == "sell"
    with pytest.raises(ValueError):
        normalize_side("hold")


def test_parse_number():
    assert parse_number("200") == 200.0
    assert parse_number(" 20 ") == 20.0
    assert parse_number("$1,250.50") == 1250.5
    with pytest.raises(ValueError):
        parse_number("abc")
    with pytest.raises(ValueError):
        parse_number("")


def test_calculate_pnl():
    assert calculate_pnl("buy", 200, 210, 20) == 200
    assert calculate_pnl("buy", 250, 240, 10) == -100
    assert calculate_pnl("sell", 450, 440, 10) == 100
    assert calculate_pnl("sell", 120, 125, 20) == -100
    assert calculate_pnl("buy", 430, 430, 5) == 0
    with pytest.raises(ValueError):
        calculate_pnl("hold", 100, 110, 1)


def test_summarise():
    stats = summarise([200, -100, 0, 100])
    assert stats["trades"] == 4
    assert stats["total"] == 200
    assert stats["wins"] == 2
    assert stats["losses"] == 1
    assert stats["breakeven"] == 1
    assert stats["win_rate"] == 50
    assert stats["avg_win"] == 150
    assert stats["avg_loss"] == -100


def test_summarise_no_losses():
    stats = summarise([100, 300])
    assert stats["avg_loss"] == 0
    assert stats["win_rate"] == 100