-- sql/03_analysis_queries.sql

-- Query 1: Average returns by company
SELECT 
    c.company_name,
    COUNT(*) as earnings_count,
    AVG(ea.post_return_pct) as avg_post_return,
    AVG(ea.immediate_reaction_pct) as avg_immediate_return,
    STDDEV(ea.post_return_pct) as return_volatility
FROM earnings_analysis ea
JOIN companies c ON ea. symbol = c.symbol
GROUP BY c.company_name
ORDER BY avg_post_return DESC;

-- Query 2: EPS surprise impact
SELECT 
    CASE 
        WHEN eps_surprise_pct > 5 THEN 'Beat'
        WHEN eps_surprise_pct < -5 THEN 'Miss'
        ELSE 'In-Line'
    END as eps_category,
    COUNT(*) as count,
    AVG(post_return_pct) as avg_return,
    AVG(immediate_reaction_pct) as avg_immediate
FROM earnings_analysis
WHERE eps_surprise_pct IS NOT NULL
GROUP BY eps_category;

-- Query 3: Quarterly trends
SELECT 
    strftime('%Y', earnings_date) as year,
    CASE 
        WHEN CAST(strftime('%m', earnings_date) AS INTEGER) <= 3 THEN 'Q1'
        WHEN CAST(strftime('%m', earnings_date) AS INTEGER) <= 6 THEN 'Q2'
        WHEN CAST(strftime('%m', earnings_date) AS INTEGER) <= 9 THEN 'Q3'
        ELSE 'Q4'
    END as quarter,
    AVG(post_return_pct) as avg_return,
    COUNT(*) as earnings_count
FROM earnings_analysis
GROUP BY year, quarter
ORDER BY year, quarter;