# scripts/day2_yahoo_only.py
"""
Day 2: Collect data for all 6 companies using ONLY Yahoo Finance
NO API RATE LIMITS! Fast and reliable. 
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import pandas as pd
from datetime import datetime
from config import *

# Import Yahoo Finance functions
from yahoo_finance_functions import (
    collect_all_data_yahoo,
    remove_timezone
)


# ============================================================================
# SQL DATABASE FUNCTIONS
# ============================================================================

def create_database():
    """Create SQLite database and tables"""
    print("\n" + "="*80)
    print("CREATING SQL DATABASE")
    print("="*80)
    
    # Read SQL schema
    schema_file = os.path.join(SQL_DIR, '01_create_schema.sql')
    
    if not os.path.exists(schema_file):
        print(f"   ❌ Schema file not found: {schema_file}")
        return None
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Connect to database (creates file if doesn't exist)
    print(f"\n📁 Database location: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Execute schema
    print(f"\n🔨 Creating tables...")
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"   ✅ Database schema created successfully")
        
        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n   Tables created:")
        for table in tables: 
            print(f"      - {table[0]}")
        
        return conn
        
    except Exception as e:
        print(f"   ❌ Error creating database: {e}")
        conn.close()
        return None


def load_to_sql(prices_df, earnings_df, companies_df, conn):
    """Load all data into SQL database"""
    print("\n" + "="*80)
    print("LOADING DATA INTO SQL DATABASE")
    print("="*80)
    
    try:
        # 1. Load companies
        print(f"\n1️⃣ Loading companies table...")
        if not companies_df.empty:
            print(f"   Columns: {len(companies_df.columns)}")
            companies_df.to_sql('companies', conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded {len(companies_df)} companies")
        
        # 2. Load stock prices
        print(f"\n2️⃣ Loading stock_prices table...")
        if not prices_df.empty:
            prices_clean = prices_df.copy()
            prices_clean['date'] = prices_clean['date'].astype(str)
            prices_clean.to_sql('stock_prices', conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded {len(prices_clean):,} price records")
        
        # 3. Load earnings dates
        print(f"\n3️⃣ Loading earnings_dates table...")
        if not earnings_df.empty:
            earnings_clean = earnings_df.copy()
            earnings_clean['date'] = earnings_clean['date'].astype(str)
            earnings_clean.to_sql('earnings_dates', conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded {len(earnings_clean)} earnings events")
        
        conn.commit()
        print(f"\n✅ All data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading data:  {e}")
        import traceback
        traceback.print_exc()
        return False


def calculate_all_metrics(conn):
    """Calculate metrics for ALL earnings events"""
    print("\n" + "="*80)
    print("CALCULATING METRICS FOR ALL EARNINGS EVENTS")
    print("="*80)
    
    # Load data from SQL
    prices_df = pd.read_sql("SELECT * FROM stock_prices", conn)
    earnings_df = pd.read_sql("SELECT * FROM earnings_dates", conn)
    
    print(f"\n🔍 Earnings columns: {earnings_df.columns.tolist()}")
    
    # Handle column name
    if 'earnings_date' in earnings_df.columns:
        date_col = 'earnings_date'
    elif 'date' in earnings_df.columns:
        earnings_df = earnings_df.rename(columns={'date': 'earnings_date'})
    else:
        print(f"❌ No date column found!")
        return pd.DataFrame()
    
    # Convert dates and remove timezone
    print(f"\n📅 Converting dates...")
    prices_df['date'] = pd.to_datetime(prices_df['date'].astype(str))
    earnings_df['earnings_date'] = pd.to_datetime(earnings_df['earnings_date'].astype(str))
    
    print(f"\n📊 Data loaded:")
    print(f"   Prices: {len(prices_df):,} records")
    print(f"   Earnings: {len(earnings_df)} events")
    
    # Calculate metrics
    all_metrics = []
    
    for idx, earnings_row in earnings_df.iterrows():
        symbol = earnings_row['symbol']
        earnings_date = earnings_row['earnings_date']
        
        if pd.isna(earnings_date):
            continue
        
        print(f"[{idx+1}/{len(earnings_df)}] {symbol} on {earnings_date.date()}.. .", end=" ")
        
        # Get prices for this symbol
        symbol_prices = prices_df[prices_df['symbol'] == symbol].copy()
        
        if symbol_prices.empty:
            print("⚠️ No prices")
            continue
        
        symbol_prices = symbol_prices.sort_values('date')
        
        # Filter by date
        try:
            prices_before = symbol_prices[symbol_prices['date'] < earnings_date]
            prices_after = symbol_prices[symbol_prices['date'] >= earnings_date]
        except Exception as e:
            print(f"⚠️ Error:  {e}")
            continue
        
        if len(prices_before) < PRE_EARNINGS_DAYS + 1 or len(prices_after) < POST_EARNINGS_DAYS: 
            print("⚠️ Not enough data")
            continue
        
        # Get windows
        pre_window = prices_before.tail(PRE_EARNINGS_DAYS + 1)
        post_window = prices_after.head(POST_EARNINGS_DAYS + 1)
        
        # Calculate returns
        pre_return = ((pre_window.iloc[-1]['close'] - pre_window.iloc[0]['close']) / pre_window.iloc[0]['close']) * 100
        post_return = ((post_window.iloc[-1]['close'] - post_window.iloc[0]['close']) / post_window.iloc[0]['close']) * 100
        total_return = ((post_window.iloc[-1]['close'] - pre_window.iloc[0]['close']) / pre_window.iloc[0]['close']) * 100
        
        immediate_return = None
        if len(post_window) > 1:
            immediate_return = ((post_window.iloc[1]['close'] - post_window.iloc[0]['close']) / post_window.iloc[0]['close']) * 100
        
        # Reaction category
        if immediate_return and immediate_return > 2: 
            reaction = "Strong Positive"
        elif immediate_return and immediate_return > 0:
            reaction = "Positive"
        elif immediate_return and immediate_return > -2:
            reaction = "Negative"
        else:
            reaction = "Strong Negative"
        
        # EPS (Yahoo Finance columns)
        eps_surprise_pct = None
        if 'Surprise(%)' in earnings_row.index and pd.notna(earnings_row['Surprise(%)']):
            eps_surprise_pct = earnings_row['Surprise(%)']
        elif 'Reported EPS' in earnings_row.index and 'EPS Estimate' in earnings_row.index:
            reported = earnings_row['Reported EPS']
            estimated = earnings_row['EPS Estimate']
            if pd.notna(reported) and pd.notna(estimated) and estimated != 0:
                eps_surprise_pct = ((reported - estimated) / abs(estimated)) * 100
        
        # EPS category
        eps_category = "Unknown"
        if pd.notna(eps_surprise_pct):
            if eps_surprise_pct > 5:
                eps_category = "Beat"
            elif eps_surprise_pct < -5:
                eps_category = "Miss"
            else:
                eps_category = "In-Line"
        
        # Save metric
        all_metrics.append({
            'symbol': symbol,
            'earnings_date': earnings_date,
            'pre_start_date': pre_window.iloc[0]['date'],
            'post_end_date': post_window.iloc[-1]['date'],
            'pre_start_price': pre_window.iloc[0]['close'],
            'earnings_price': pre_window.iloc[-1]['close'],
            'post_end_price': post_window.iloc[-1]['close'],
            'pre_return_pct': pre_return,
            'post_return_pct': post_return,
            'immediate_return_pct': immediate_return,
            'total_return_pct': total_return,
            'eps_surprise_pct': eps_surprise_pct,
            'eps_category': eps_category,
            'reaction_category': reaction,
            'year': earnings_date.year,
            'quarter': earnings_date.quarter,
            'year_quarter': f"{earnings_date.year}-Q{earnings_date.quarter}",
            'pre_days_actual': len(pre_window) - 1,
            'post_days_actual': len(post_window) - 1
        })
        
        print(f"✅ {post_return:+.1f}%")
    
    # Create DataFrame
    metrics_df = pd.DataFrame(all_metrics)
    
    if not metrics_df.empty:
        print(f"\n✅ Calculated {len(metrics_df)} earnings events")
        
        # Convert dates to strings for SQL
        metrics_df['earnings_date'] = metrics_df['earnings_date'].astype(str)
        metrics_df['pre_start_date'] = metrics_df['pre_start_date'].astype(str)
        metrics_df['post_end_date'] = metrics_df['post_end_date'].astype(str)
        
        metrics_df.to_sql('earnings_analysis', conn, if_exists='replace', index=False)
        print(f"✅ Saved to database")
    
    return metrics_df


def export_for_powerbi(conn):
    """Export clean CSV files for Power BI"""
    print("\n" + "="*80)
    print("EXPORTING DATA FOR POWER BI")
    print("="*80)
    
    tables = ['companies', 'stock_prices', 'earnings_dates', 'earnings_analysis']
    
    for table in tables:
        print(f"\n📤 Exporting {table}...")
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            output_file = os.path.join(POWERBI_DATA_DIR, f"{table}.csv")
            df.to_csv(output_file, index=False)
            print(f"   ✅ Saved:  {output_file}")
            print(f"   Records: {len(df):,}")
        except Exception as e: 
            print(f"   ⚠️ Skipping {table}: {e}")
    
    print(f"\n✅ All exports complete!")
    print(f"📁 Location: {POWERBI_DATA_DIR}")


def generate_summary(conn):
    """Generate summary statistics"""
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    cursor = conn.cursor()
    
    # Overall stats
    print("\n📊 Overall Statistics:")
    
    cursor.execute("SELECT COUNT(*) FROM companies")
    print(f"   Companies analyzed: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM stock_prices")
    print(f"   Price records: {cursor.fetchone()[0]: ,}")
    
    cursor.execute("SELECT COUNT(*) FROM earnings_dates")
    print(f"   Earnings events: {cursor.fetchone()[0]}")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM earnings_analysis")
        print(f"   Analyzed events: {cursor.fetchone()[0]}")
        
        # Performance by company
        print("\n📈 Performance by Company:")
        df = pd.read_sql("""
            SELECT 
                symbol,
                COUNT(*) as earnings_count,
                ROUND(AVG(post_return_pct), 2) as avg_return,
                ROUND(AVG(immediate_return_pct), 2) as avg_immediate,
                ROUND(SUM(CASE WHEN post_return_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as win_rate
            FROM earnings_analysis
            GROUP BY symbol
            ORDER BY avg_return DESC
        """, conn)
        
        print(df.to_string(index=False))
        
        # Reaction categories
        print("\n📊 Reaction Categories:")
        df = pd.read_sql("""
            SELECT 
                reaction_category,
                COUNT(*) as count,
                ROUND(AVG(post_return_pct), 2) as avg_return
            FROM earnings_analysis
            GROUP BY reaction_category
            ORDER BY avg_return DESC
        """, conn)
        
        print(df.to_string(index=False))
        
    except Exception as e:
        print(f"   ⚠️ Analysis table not yet created")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution for Day 2 - Yahoo Finance Only"""
    start_time = datetime.now()
    
    print("\n" + "="*80)
    print("DAY 2: MULTI-COMPANY ANALYSIS (YAHOO FINANCE ONLY)")
    print("="*80)
    print("\n✅ Using Yahoo Finance - NO API RATE LIMITS!")
    print("="*80)
    
    # Step 1: Collect data from Yahoo Finance
    prices_df, earnings_df, companies_df = collect_all_data_yahoo(COMPANIES)
    
    if prices_df.empty or earnings_df.empty:
        print("\n❌ Failed to collect sufficient data")
        return
    
    # Step 2: Create database
    conn = create_database()
    
    if not conn:
        print("\n❌ Failed to create database")
        return
    
    # Step 3: Load to SQL
    success = load_to_sql(prices_df, earnings_df, companies_df, conn)
    
    if not success:
        print("\n❌ Failed to load data to SQL")
        conn.close()
        return
    
    # Step 4: Calculate metrics
    metrics_df = calculate_all_metrics(conn)
    
    # Step 5: Export for Power BI
    export_for_powerbi(conn)
    
    # Step 6: Summary
    generate_summary(conn)
    
    # Close connection
    conn.close()
    
    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("✅ DAY 2 COMPLETE!")
    print("="*80)
    print(f"\n⏱️ Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"\n📁 Database:  {DATABASE_PATH}")
    print(f"📁 Power BI exports: {POWERBI_DATA_DIR}")
    print(f"\n📊 Data Source: Yahoo Finance (no API limits! )")
    print("\nNext steps:")
    print("   1. Explore database with SQL queries")
    print("   2. Import CSV files into Power BI")
    print("   3. Create dashboards!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()