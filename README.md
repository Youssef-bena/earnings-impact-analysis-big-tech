# 📊 Earnings Reaction Analysis (API → SQL → Power BI)

⏱️ *Estimated reading time: 3 minutes*

This project analyzes how stock prices react to **quarterly earnings announcements** using an **end-to-end analytics pipeline**:  
API ingestion → data cleaning → SQL modeling → interactive Power BI dashboard.

**Scope:** 6 Big Tech companies (AAPL, MSFT, GOOGL, AMZN, META, TSLA) • 2022–2026 • ±5 trading days  
**Deliverables:** Python scripts • SQLite database • Power BI dashboard  
**Disclaimer:** Educational project only — not financial advice.

---

## 👋 Who this project is for

- **Recruiters / Hiring Managers** → focus on *Business Questions*, *Key Results*, and *Dashboard Preview*  
- **Technical reviewers** → jump to *Technical Deep Dive* (Python / SQL links)

---

## 🎯 Business Questions Answered

1. Do stocks tend to rise after **earnings beats vs misses**?
2. Which companies show the **most consistent post-earnings behavior**?
3. How often does **“sell the news”** occur?
4. How strong is the link between **EPS surprise and price reaction**?
5. Are there **temporal patterns** (year / quarter) in earnings reactions?

---

## 📊 Dashboard Preview (Power BI)

✅ **Yes — 5 screenshots is perfectly acceptable** when each page answers a different question.

![Executive Summary](data/processed/visualizations/dashboard_preview-1.png)  
*High-level KPIs and overall earnings impact*

![Company Deep Dive](data/processed/visualizations/dashboard_preview-2.png)  
*Per-company performance and volatility*

![EPS Surprise Analysis](data/processed/visualizations/dashboard_preview-3.png)  
*Beat vs Miss impact and “sell the news” cases*

![Time Trends](data/processed/visualizations/dashboard_preview-4.png)  
*Quarterly and yearly reaction patterns*

![Detailed Explorer](data/processed/visualizations/dashboard_preview-5.png)  
*Event-level drill-down and filtering*

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

- Translating vague questions into **structured analysis**
- Ownership of an **end-to-end data pipeline**
- Handling **messy, real-world financial data**
- Communicating **insights + limitations clearly**
- Building **decision-oriented dashboards**

---

## 🧠 Technical Deep Dive (for data & engineering profiles)

### 🐍 Python
- Data collection: [`scripts/collect_data.py`](scripts/collect_data.py)
- Metric calculation: [`scripts/calculate_metrics.py`](scripts/calculate_metrics.py)

### 🗄️ SQL
- Schema definition: [`sql/schema.sql`](sql/schema.sql)
- Analysis queries: [`sql/queries.sql`](sql/queries.sql)

### 📊 Power BI
- Dashboard file: `dashboards/Earnings_Analysis_Dashboard.pbix`
- Star schema & measures: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)

---

## 🧠 Methodology (Summary)

For each earnings event:
- Collect daily prices around the announcement
- Compute pre/post earnings returns and EPS surprise
- Categorize outcomes (Beat / In-Line / Miss)

📘 Full methodology: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)

---

## 📁 Repository Structure

```
├── scripts/
├── sql/
├── data/sample/
├── notebooks/
├── visualizations/
└── docs/
```

---

## 🚀 Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python scripts/collect_data.py
python scripts/calculate_metrics.py
```

---

## ⚠️ Limitations

- Small sample size (quarterly events only)
- External news can dominate price movements
- EPS alone does not explain returns
- Descriptive, not predictive

---

## 📞 Contact

**Youssef Ben Abdallah**  
📧 youssef.bena.it@gmail.com  
💼 https://www.linkedin.com/in/youssefbena/  
💻 https://github.com/Youssef-bena  

---

## 📄 License

MIT — see [`LICENSE`](LICENSE).
