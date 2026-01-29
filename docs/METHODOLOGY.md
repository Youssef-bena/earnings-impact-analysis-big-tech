\# Methodology



This project measures how stock prices react to quarterly earnings announcements.



\## Approach

\- Collect daily prices and earnings dates from Yahoo Finance

\- Analyze ±5 trading days around each earnings event

\- Compute post-earnings returns and EPS surprise

\- Store results in a SQLite database

\- Visualize insights in Power BI



\## Key Definitions

\- Post-earnings return: % change over 5 trading days after earnings : 100 \*(5days after earnings - earnings price) / earnings price

\- immediate return: % change over 5 trading days after earnings : 100 \*(day after earnings - earnings price) / earnings price

\- EPS Surprise: (Actual − Estimate) / |Estimate|



\## Assumptions \& Limitations

\- Earnings are analyzed independently

\- Other market news may influence price movements

\- Results are descriptive, not predictive



