# 🧠 Technical Details

## Architecture
API → Python ETL → SQLite Database → Power BI Dashboard

## Python
- Data ingestion with yfinance
- Cleaning: timezone normalization, missing data handling
- Metric computation and categorization

## SQL
- Star schema design
- Fact table: earnings analysis
- Dimension tables: companies, dates, categories

## Power BI
- Star schema model
- ~30 DAX measures
- Interactive slicers and drill-through

## Challenges Solved
- API rate limits
- Timezone inconsistencies
- Missing EPS data
- DAX filter context issues
