# Trade Analyzer
#### Description:
Most brokers let you export your trade history as a CSV file, but every broker names and formats the columns differently: one calls it "Ticker", another "Symbol"; one writes "Buy", another "B" or "Long"; prices can come as `200` or `$1,250.50`. Trade Analyzer reads trade CSVs from different sources, normalizes them into one standard format, and reports the P&L of every trade along with summary statistics: total P&L, number of wins, losses and breakeven trades, win rate, average win and average loss.

## How to run
```
python project.py your_trades.csv
```
Example output for a 12-trade file (last lines):
```
2026-07-30  AAPL   sell +150.00

Trades:       12
Total P&L:    +890.00
Wins/Losses/Breakeven: 7/4/1
Win rate:     58.33%
Average win:  +184.29
Average loss: -100.00
```

## Files
### project.py
The main program. At the top are two alias dictionaries, `HEADER_ALIASES` and `SIDE_ALIASES`, which list the accepted variants for each standard column name and for buy/sell.

- `main()` checks the command-line argument (exactly one file, ending in `.csv`), loads the trades, prints each trade's P&L and then the summary.
- `normalize_header(name)` cleans a column name (strip and lowercase) and returns its standard name, e.g. `" Entry Price "` → `"entry"`. Unknown columns return `None` and are ignored.
- `normalize_side(value)` turns a side such as `"Long"`, `"S"` or `"SOLD"` into `"buy"` or `"sell"`, and raises `ValueError` if the side is unknown.
- `parse_number(text)` removes `$`, commas and spaces and converts the text to a float.
- `calculate_pnl(side, entry, exit, quantity)` returns the P&L of one trade: `(exit - entry) * quantity` for buys and `(entry - exit) * quantity` for sells.
- `load_trades(filename)` opens the file, maps its headers to standard names, checks that all six required columns exist, cleans every row and returns a list of trade dictionaries.
- `summarise(pnls)` takes a list of P&Ls and returns a dictionary of statistics.

### test_project.py
Tests for `normalize_header`, `normalize_side`, `parse_number`, `calculate_pnl` and `summarise`, using pytest. Each function is tested on normal inputs, edge cases (extra spaces, mixed case, breakeven trades, no losing trades) and invalid inputs that should raise `ValueError`.

### requirements.txt
Lists `pytest`, the only library that needs installing. `csv` and `sys` are part of Python's standard library.

### Input files
Sample CSVs are not included in this repository. Any CSV with a date, symbol, side, entry price, exit price and quantity column works, as long as the headers match one of the aliases in `HEADER_ALIASES` (for example `Ticker`, `Direction`, `Entry Price`, `Close`, `Qty`). I tested the program on files imitating different brokers: alternative header names, `B`/`S` sides, extra columns such as fees and notes, dollar signs and thousands separators, timestamps, fractional shares, and a file with an invalid side that should make the program stop.

## Design choices
**Alias dictionaries instead of one fixed format.** Rather than requiring a specific layout, the program compares each cleaned header and side against a list of known variants. Supporting a new broker usually just means adding a word to a list.

**`None` versus `ValueError`.** An unknown column (like "Fees") is harmless, so `normalize_header` returns `None` and the column is skipped. An unknown side makes the P&L impossible to calculate, so `normalize_side` raises an error.

**Fail fast.** Missing columns are detected before any row is read, and the program exits with a message naming them. A bad value stops the program with its line number instead of silently skipping the row or producing wrong statistics.

**Breakeven trades.** A trade with a P&L of exactly zero is counted separately and not as a win, so the win rate is wins divided by all trades.

**`csv.DictReader` instead of pandas.** The standard library was enough for this task and keeps the project free of heavy dependencies.

## Limitations
- Some aliases are ambiguous: "Open" could mean the open price or the open time.
- Headers with underscores or hyphens (e.g. `Entry_Price`) are not matched unless added to the alias lists.
- Fees, commissions and partial fills are ignored.
- Values containing commas must be quoted in the CSV, as real broker exports do.
