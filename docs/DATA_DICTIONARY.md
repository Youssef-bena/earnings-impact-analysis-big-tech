# Data Dictionary for Earnings Analysis

## File:  earnings_analysis.csv (MAIN FILE)

| Column | Type | Description | Example | Use in Power BI |
|--------|------|-------------|---------|-----------------|
| `symbol` | Text | Stock ticker | "AAPL" | Filter, Group By |
| `earnings_date` | Date | Earnings announcement date | "2024-10-31" | Timeline, Filter |
| `pre_start_date` | Date | Start of pre-earnings window | "2024-10-24" | Reference |
| `post_end_date` | Date | End of post-earnings window | "2024-11-07" | Reference |
| `pre_start_price` | Number | Stock price 5 days before | 230.50 | Calculation |
| `earnings_price` | Number | Stock price on earnings day | 226.25 | Calculation |
| `post_end_price` | Number | Stock price 5 days after | 230.30 | Calculation |
| **`pre_return_pct`** | **Number** | **Return before earnings (%)** | -1.84 | **Chart Axis** |
| **`post_return_pct`** | **Number** | **Return after earnings (%)** | +1.79 | **Main KPI** |
| **`immediate_return_pct`** | Number | Day-1 reaction (%) | +0.77 | Secondary KPI |
| `total_return_pct` | Number | Total 10-day return (%) | -0.09 | Analysis |
| **`eps_surprise_pct`** | Number | EPS beat/miss (%) | +5.8 | Filter, Color |
| **`eps_category`** | Text | "Beat", "Miss", "In-Line" | "Beat" | Slicer, Filter |
| **`reaction_category`** | Text | Stock reaction label | "Positive" | Slicer, Color |
| `year` | Number | Year of earnings | 2024 | Timeline |
| `quarter` | Number | Quarter (1-4) | 4 | Filter |
| `year_quarter` | Text | Combined label | "2024-Q4" | Timeline |
| `pre_days_actual` | Number | Actual pre-days | 5 | Quality Check |
| `post_days_actual` | Number | Actual post-days | 5 | Quality Check |

### Recommended Measures (DAX):

```dax
Avg Post Return = AVERAGE(earnings_analysis[post_return_pct])
Win Rate = DIVIDE(COUNTROWS(FILTER(earnings_analysis, [post_return_pct] > 0)), COUNTROWS(earnings_analysis))
Total Events = COUNTROWS(earnings_analysis)
Best Reaction = MAX(earnings_analysis[post_return_pct])
Worst Reaction = MIN(earnings_analysis[post_return_pct])