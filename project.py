import csv
import sys

HEADER_ALIASES = {
    "date": ["date", "trade date", "datetime", "time", "timestamp", "open date"],
    "symbol": ["symbol", "ticker", "instrument", "stock", "asset", "security"],
    "side": ["side", "direction", "action", "type", "buy/sell", "trade type"],
    "entry": ["entry", "entry price", "open", "open price", "buy price", "price in"],
    "exit": ["exit", "exit price", "close", "close price", "sell price", "price out"],
    "quantity": ["quantity", "qty", "shares", "size", "volume", "amount", "units"],
}

SIDE_ALIASES = {
    "buy": ["buy", "b", "bought", "long", "l"],
    "sell": ["sell", "s", "sold", "short", "sh"],
}

def main():
    if len(sys.argv) < 2:
        sys.exit("Too few arguments")
    if len(sys.argv) > 2:
        sys.exit("Too many arguments")
    if not sys.argv[1].lower().endswith(".csv"):
        sys.exit("File should be a CSV")

    trades = load_trades(sys.argv[1])

    pnls = []
    for trade in trades:
        pnl = calculate_pnl(trade["side"], trade["entry"], trade["exit"], trade["quantity"])
        print(f"{trade['date']}  {trade['symbol']:<6} {trade['side']:<4} {pnl:+.2f}")
        pnls.append(pnl)

    stats = summarise(pnls)

    print()
    print(f"Trades:       {stats['trades']}")
    print(f"Total P&L:    {stats['total']:+.2f}")
    print(f"Wins/Losses/Breakeven: {stats['wins']}/{stats['losses']}/{stats['breakeven']}")
    print(f"Win rate:     {stats['win_rate']:.2f}%")
    print(f"Average win:  {stats['avg_win']:+.2f}")
    print(f"Average loss: {stats['avg_loss']:+.2f}")

def normalize_side(value):
    """convers side like Long or S to buy or sell and raises ValueError if its unknown"""
    value = value.strip().lower()
    for standard, variants in SIDE_ALIASES.items():
        if value in variants:
            return standard
    raise ValueError (f"Unknown side: {value}")

def normalize_header(name):
    """convert column name to standard name like 'entry' """
    name = name.strip().lower()
    for standard, variants in HEADER_ALIASES.items():
        if name in variants:
            return standard
    return None  


def parse_number(text):
    """convert a number string to a float whilst removing $ and "," elements"""
    return float(text.replace("$", "").replace(",","").strip())


def calculate_pnl(side, entry, exit, quantity):
    """calculate the pnl of one trade"""
    if side == "buy":
        return float((exit - entry) * quantity)
    if side == "sell":
        return float((entry - exit) * quantity)
    raise ValueError ("There is no PNL")
def load_trades(filename):
    """Read a CSV of trades, map its headers to standardized names, cleans every row and returns a list of trade dictionaries, exits with clear message in case of error"""
    try:
        with open(filename) as file:
            reader = csv.DictReader(file)
            mapping = {}
            for original in reader.fieldnames:
                standard = normalize_header(original)
                if standard is not None:
                    mapping[original] = standard

            missing = set(HEADER_ALIASES) - set(mapping.values())
            if missing:
                sys.exit(f"Missing columns: {', '.join(missing)}")

            trades = []
            for line, row in enumerate(reader, start=2):
                trade = {}
                for original, standard in mapping.items():
                    trade[standard] = row[original]

                try:
                    trade["side"] = normalize_side(trade["side"])
                    trade["entry"] = parse_number(trade["entry"])
                    trade["exit"] = parse_number(trade["exit"])
                    trade["quantity"] = parse_number(trade["quantity"])
                except ValueError:
                    sys.exit(f"Bad Value on line {line}")

                trade["symbol"] = trade["symbol"].strip().upper()
                trades.append(trade)
    except FileNotFoundError:
        sys.exit("File does not exist")
    return trades
def summarise(pnls):
    """Return a dictionary of stats from a list of PnLs: trade count, total, wins, losses, breakeven, win_rate, avg_win, avg_loss"""
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    breakeven = [p for p in pnls if p == 0]

    win_rate = len(wins) / len(pnls) * 100
    avg_win = sum(wins) / len(wins)
    avg_loss = sum(losses) / len(losses) if losses else 0

    return {
        "trades": len(pnls),
        "total": sum(pnls),
        "wins": len(wins),
        "losses": len(losses),
        "breakeven": len(breakeven),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
    }


if __name__ == "__main__":
    main()