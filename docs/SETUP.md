# ⚙️ Setup Guide

## Prerequisites
- Python 3.8+
- Power BI Desktop (optional for dashboard)

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Project
```bash
python scripts/collect_data.py
python scripts/calculate_metrics.py
```

## Power BI
- Open `Earnings_Analysis_Dashboard.pbix`
- Load data from CSVs or refresh if connected

## Notes
- All data is public and free
- Scripts are fully reproducible
