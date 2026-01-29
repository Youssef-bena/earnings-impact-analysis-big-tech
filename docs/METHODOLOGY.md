# 📘 Methodology

## Objective

Analyze how stock prices react to quarterly earnings announcements and determine whether earnings surprises (beats/misses) influence short-term market movements.

## Data Sources

* **Stock prices \& earnings data:** Yahoo Finance (via yfinance)
* **Companies analyzed:** AAPL, MSFT, GOOGL, AMZN, META, TSLA
* **Period:** 2022–2026

## Analysis Window

* **Pre-earnings:** 5 trading days before announcement
* **Post-earnings:** 5 trading days after announcement
  This window balances immediate reaction and delayed market adjustment while limiting noise.

## Metrics

* Pre-earnings return (%)
* Post-earnings return (%)
* Immediate reaction (next trading day)
* EPS surprise (%)

## Categorization

* **EPS:** Beat (>5%), In-Line (±5%), Miss (<-5%)
* **Price reaction:** Strong Positive, Positive, Negative, Strong Negative

## Limitations

* Quarterly data → small sample size
* External news may influence price movements
* Analysis is descriptive, not predictive
