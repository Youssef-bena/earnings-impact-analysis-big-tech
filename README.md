# 📊 Earnings Reaction Analysis (API → SQL → Power BI)

⏱️ *Estimated reading time: 3 minutes*

Measure how stock prices react to quarterly earnings announcements using an **end-to-end analytics pipeline**:  
data ingestion (Yahoo Finance) → cleaning & feature engineering (Python) → storage & querying (SQLite) → interactive reporting (Power BI).

**Scope:** 6 Big Tech companies (AAPL, MSFT, GOOGL, AMZN, META, TSLA) • 2022–2026 • ±5 trading days around each earnings date  
**Deliverables:** SQLite database • reproducible Python/SQL scripts • Power BI dashboard  
**Disclaimer:** Educational project only — not financial advice.

---

## 🎯 Business Questions Answered

1. **Do stocks tend to rise after “beats” vs “misses”?**  
2. **Which companies show the most consistent post-earnings behavior?**  
3. **How often does “sell the news” occur?**  
4. **How strong is the link between EPS surprise and price reaction?**  
5. **Are there time patterns (year / quarter) in earnings reactions?**

---

## 📊 Dashboard Preview (Power BI)

![Executive Summary](data/processed/visualizations/dashboard_preview-1.png)  
![Company Deep Dive](data/processed/visualizations/dashboard_preview-2.png)  
![EPS Surprise Analysis](data/processed/visualizations/dashboard_preview-3.png)  
![Time Trends](data/processed/visualizations/dashboard_preview-4.png)  
![Detailed Explorer](data/processed/visualizations/dashboard_preview-5.png)

---

## 🔑 Key Results (High-Level)

- **Beating earnings helps — but modestly**  
  Average post-earnings return of **+1.22%** for beats vs **-1.16%** for misses.

- **Company behavior matters more than timing**  
  Some companies react consistently, others remain highly volatile.

- **Tesla stands out**  
  +2.24% average return per earnings, **56.25% win rate**.

- **Google underperforms**  
  -0.59% average return despite frequently beating expectations.

- **“Sell the news” is real**  
  A meaningful share of earnings beats still lead to negative returns.

- **Predictability is limited**  
  Overall win rate of **~54%**, barely better than a coin flip.

**Bottom line:** *Earnings create volatility, not reliable profits. Company selection matters more than timing.*

---

## 🧩 What This Project Demonstrates

- **Data acquisition:** API ingestion (yfinance) and handling missing / uneven fields  
- **Data engineering:** cleaning, type enforcement, timezone normalization, validation  
- **Analytics:** metric design (pre/post windows), categorization, outlier handling  
- **SQL:** schema design, constraints, indexes, analytical queries  
- **BI:** star-schema modeling, DAX measures, dashboard UX & interactivity  
- **Communication:** clear insights, assumptions, and limitations

---

## 🗂️ Data Sources

- **Prices & earnings:** Yahoo Finance via `yfinance` (4,500+ daily prices)  
- **Period:** 2022-01-01 → 2026-01-16  
- **Window:** 5 trading days before + 5 trading days after earnings

---

## 🗃️ Repository Structure

```
├── scripts/              # data collection, metric calculation, exports
├── sql/                  # database schema & queries
├── data/sample/          # small sample datasets
├── notebooks/            # optional exploration notebooks
├── visualizations/       # charts & dashboard screenshots
└── docs/                 # methodology, insights, technical notes
```

---

## 🧠 Methodology (Summary)

For each earnings event:
- Collect daily prices around the event date  
- Compute:
  - **Pre-earnings return** (5 days before)
  - **Post-earnings return** (5 days after)
  - **Immediate reaction** (next trading day)
  - **EPS surprise %** = (Actual − Estimate) / |Estimate| × 100  
- Categorize:
  - EPS: **Beat / In-line / Miss**
  - Reaction: **Strong positive / positive / negative / strong negative**

📘 Full details: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)

---

## 🚀 Quickstart (Reproducible)

### 1️⃣ Install
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

### 2️⃣ Run the pipeline
```bash
python scripts/collect_data.py
python scripts/calculate_metrics.py
```

### 3️⃣ Open the dashboard
- Open `dashboards/Earnings_Analysis_Dashboard.pbix` in Power BI Desktop  
- Refresh or load from exported CSVs (see `docs/SETUP.md`)

📄 Full setup guide: [`docs/SETUP.md`](docs/SETUP.md)

---

## 🧮 Sample SQL Query

```sql
-- Which companies have the best post-earnings track record?
SELECT 
  symbol,
  COUNT(*) AS earnings_count,
  ROUND(AVG(post_return_pct), 2) AS avg_return,
  ROUND(
    SUM(CASE WHEN post_return_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    1
  ) AS win_rate
FROM earnings_analysis
GROUP BY symbol
ORDER BY avg_return DESC;
```

🔗 More queries: [`sql/queries.sql`](sql/queries.sql)

---

## ⚠️ Limitations

- Small sample size per company (quarterly events only)  
- Market reactions influenced by external news and sentiment  
- EPS alone does not explain price movement  
- Analysis is descriptive, not predictive

---

## 🔮 Next Steps

- Expand to more companies and sectors  
- Add additional explanatory variables (guidance, sentiment)  
- Build and evaluate ML models with proper validation  
- Automate data refresh and dashboard updates

---

## 📞 Contact

**Youssef Ben Abdallah**  
📧 Email: youssef.bena.it@gmail.com  
💼 LinkedIn: https://www.linkedin.com/in/youssefbena/  
💻 GitHub: https://github.com/Youssef-bena  

---

## 📄 License

MIT — see [`LICENSE`](LICENSE).
