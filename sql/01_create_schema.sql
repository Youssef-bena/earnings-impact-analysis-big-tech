-- sql/01_create_schema.sql
/*
Database schema for Earnings Analysis Project
Simplified and tested version
*/

-- Drop everything first (clean slate)
DROP VIEW IF EXISTS v_quarterly_trends;
DROP VIEW IF EXISTS v_eps_performance;
DROP VIEW IF EXISTS v_company_stats;
DROP VIEW IF EXISTS v_earnings_performance;
DROP VIEW IF EXISTS v_company_overview;
DROP TABLE IF EXISTS earnings_analysis;
DROP TABLE IF EXISTS earnings_dates;
DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS companies;

-- ============================================================================
-- TABLE 1: COMPANIES
-- ============================================================================

CREATE TABLE companies (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    currency TEXT,
    exchange TEXT,
    exchangeFullName TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE 2: STOCK PRICES
-- ============================================================================

CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL NOT NULL,
    volume INTEGER,
    adjClose REAL,
    change REAL,
    changePercent REAL,
    vwap REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

CREATE INDEX idx_stock_prices_symbol_date ON stock_prices(symbol, date);

-- ============================================================================
-- TABLE 3: EARNINGS DATES
-- ============================================================================

CREATE TABLE earnings_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_earnings_dates_symbol_date ON earnings_dates(symbol, date);

-- ============================================================================
-- TABLE 4: EARNINGS ANALYSIS
-- ============================================================================

CREATE TABLE earnings_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    earnings_date TEXT NOT NULL,
    pre_start_date TEXT,
    post_end_date TEXT,
    pre_start_price REAL,
    earnings_price REAL,
    post_end_price REAL,
    pre_return_pct REAL,
    post_return_pct REAL,
    immediate_return_pct REAL,
    total_return_pct REAL,
    eps_surprise_pct REAL,
    eps_category TEXT,
    reaction_category TEXT,
    year INTEGER,
    quarter INTEGER,
    year_quarter TEXT,
    pre_days_actual INTEGER,
    post_days_actual INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_earnings_analysis_symbol_date ON earnings_analysis(symbol, earnings_date);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View 1: Company Overview
CREATE VIEW v_company_overview AS
SELECT 
    c. symbol,
    c.name,
    c.exchange,
    c.exchangeFullName,
    c.currency,
    (SELECT close FROM stock_prices sp WHERE sp.symbol = c.symbol ORDER BY date DESC LIMIT 1) as latest_price,
    (SELECT date FROM stock_prices sp WHERE sp. symbol = c.symbol ORDER BY date DESC LIMIT 1) as latest_price_date
FROM companies c;

-- View 2: Earnings Performance
CREATE VIEW v_earnings_performance AS
SELECT 
    ea.symbol,
    c.name as company_name,
    ea. earnings_date,
    ea. pre_return_pct,
    ea. post_return_pct,
    ea.immediate_return_pct,
    ea.eps_surprise_pct,
    ea.eps_category,
    ea.reaction_category,
    ea.year_quarter
FROM earnings_analysis ea
LEFT JOIN companies c ON ea.symbol = c.symbol
ORDER BY ea.earnings_date DESC;

-- View 3: Company Stats
CREATE VIEW v_company_stats AS
SELECT 
    ea.symbol,
    c.name as company_name,
    COUNT(*) as total_earnings,
    ROUND(AVG(ea.post_return_pct), 2) as avg_post_return,
    ROUND(AVG(ea.immediate_return_pct), 2) as avg_immediate_return,
    ROUND(MIN(ea.post_return_pct), 2) as min_return,
    ROUND(MAX(ea.post_return_pct), 2) as max_return,
    ROUND(SUM(CASE WHEN ea.post_return_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as win_rate_pct
FROM earnings_analysis ea
LEFT JOIN companies c ON ea.symbol = c.symbol
GROUP BY ea.symbol, c.name;

-- View 4: EPS Performance
CREATE VIEW v_eps_performance AS
SELECT 
    eps_category,
    COUNT(*) as count,
    ROUND(AVG(post_return_pct), 2) as avg_return,
    ROUND(AVG(immediate_return_pct), 2) as avg_immediate_return
FROM earnings_analysis
WHERE eps_category IS NOT NULL
GROUP BY eps_category;

-- View 5: Quarterly Trends
CREATE VIEW v_quarterly_trends AS
SELECT 
    year_quarter,
    COUNT(*) as earnings_count,
    ROUND(AVG(post_return_pct), 2) as avg_return,
    SUM(CASE WHEN eps_category = 'Beat' THEN 1 ELSE 0 END) as beats,
    SUM(CASE WHEN eps_category = 'Miss' THEN 1 ELSE 0 END) as misses
FROM earnings_analysis
WHERE year_quarter IS NOT NULL
GROUP BY year_quarter
ORDER BY year_quarter;