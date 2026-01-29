# scripts/day1_test_apple_hybrid.py
"""
Day 1: Hybrid approach - FMP for prices, Yahoo Finance for earnings
This demonstrates real-world data engineering:  using multiple sources
"""

import sys
import os
sys.path.append(os.path.dirname(os. path.dirname(os.path. abspath(__file__))))

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
from config import *


# ============================================================================
# TIMEZONE FIX HELPER
# ============================================================================

def remove_timezone(df, date_column='date'):
    """
    Remove timezone information from datetime column
    Converts tz-aware to tz-naive for comparison
    """
    if date_column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[date_column]):
            # If datetime and has timezone, remove it
            if hasattr(df[date_column]. dtype, 'tz') and df[date_column].dt.tz is not None:
                df[date_column] = df[date_column].dt. tz_localize(None)
        else:
            # Convert to datetime without timezone
            df[date_column] = pd.to_datetime(df[date_column]).dt.tz_localize(None)
    
    return df


# ============================================================================
# FMP API FUNCTIONS (for stock prices)
# ============================================================================

def make_api_request(endpoint, params=None, max_retries=3):
    """Make FMP API request with retry logic"""
    if params is None:
        params = {}
    
    params['apikey'] = API_KEY
    url = f"{BASE_URL}/{endpoint}"
    
    print(f"   Making FMP request to: {endpoint}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(f"   ✅ Success!")
            return data
            
        except requests.exceptions. Timeout:
            if attempt < max_retries - 1:
                print(f"   ⚠️ Timeout (attempt {attempt+1}/{max_retries}), retrying...")
                time.sleep(2)  # Wait before retry
                continue
            else:
                print(f"   ❌ Request timed out after {max_retries} attempts")
                return None
                
        except Exception as e: 
            print(f"   ❌ Error:  {e}")
            return None
    
    return None


def get_stock_prices_fmp(symbol):
    """
    Fetch historical stock prices from FMP API
    """
    print(f"\n📊 Fetching stock prices from FMP for {symbol}...")
    
    endpoint = ENDPOINTS['historical_eod']
    params = {'symbol': symbol, 'from': START_DATE, 'to': END_DATE}
    
    data = make_api_request(endpoint, params)
    
    if data:
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'historical' in data:
            df = pd.DataFrame(data['historical'])
        else:
            return pd.DataFrame()
        
        if df.empty:
            return pd. DataFrame()
        
        df['symbol'] = symbol
        df['date'] = pd.to_datetime(df['date'])

        df = remove_timezone(df, 'date')

        df = df.sort_values('date').reset_index(drop=True)
        
        print(f"   ✅ Retrieved {len(df)} price records from FMP")
        print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        return df
    
    return pd.DataFrame()


def get_stock_prices_yahoo(symbol):
    """Alternative:  Get stock prices from Yahoo Finance"""
    print(f"\n📊 Fetching stock prices from Yahoo Finance for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=START_DATE, end=END_DATE)
        
        if df. empty:
            print(f"   ❌ No price data")
            return pd.DataFrame()
        
        df = df.reset_index()
        
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        df['symbol'] = symbol
        df['date'] = pd.to_datetime(df['date'])
        
        # ✅ REMOVE TIMEZONE
        df = remove_timezone(df, 'date')
        
        print(f"   ✅ Retrieved {len(df)} price records from Yahoo Finance")
        print(f"   Date range: {df['date']. min().date()} to {df['date'].max().date()}")
        
        return df
        
    except Exception as e: 
        print(f"   ❌ Error:  {e}")
        return pd.DataFrame()

def get_company_info_fmp(symbol):
    """Fetch company info from FMP"""
    print(f"\n🏢 Fetching company info from FMP for {symbol}...")
    
    endpoint = ENDPOINTS['search_symbol']
    params = {'query': symbol, 'limit': 1}
    
    data = make_api_request(endpoint, params)
    
    if data and len(data) > 0:
        info = data[0]
        print(f"   ✅ {info. get('name', symbol)}")
        return info
    
    return {}


def get_company_info(symbol):
    """
    Get company info from Search Symbol API only (5 columns)
    No Quote API - avoids rate limits
    """
    print(f"\n🏢 Fetching company info for {symbol}...")
    
    # Only call Search Symbol API
    info_search = get_company_info_fmp(symbol)
    
    if info_search:
        print(f"   ✅ Got {len(info_search)} fields from Search API")
        return info_search
    else:
        # Fallback to Yahoo Finance if FMP fails
        print(f"   ⚠️ Search API failed, trying Yahoo Finance...")
        return get_company_info_yahoo(symbol)

# ============================================================================
# YAHOO FINANCE FUNCTIONS (for earnings)
# ============================================================================

def get_earnings_yahoo(symbol):
    """Fetch earnings dates from Yahoo Finance"""
    print(f"\n📅 Fetching earnings data from Yahoo Finance for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        
        print(f"   Accessing Yahoo Finance earnings calendar...")
        earnings_dates = ticker.earnings_dates
        
        if earnings_dates is None or earnings_dates.empty:
            print(f"   ⚠️ No earnings dates, trying earnings history...")
            
            earnings_history = ticker.earnings
            
            if earnings_history is not None and not earnings_history.empty:
                df = earnings_history.reset_index()
                df. columns = ['date', 'eps']
                df['date'] = pd.to_datetime(df['date'])
                df['symbol'] = symbol
                
                print(f"   ✅ Retrieved {len(df)} earnings events from earnings history")
            else:
                print(f"   ❌ No earnings data available")
                return pd.DataFrame()
        else:
            df = earnings_dates.reset_index()
            df.columns = ['date'] + list(df.columns[1:])
            df['date'] = pd.to_datetime(df['date'])
            df['symbol'] = symbol
            
            print(f"   ✅ Retrieved {len(df)} earnings events from earnings calendar")
        
        # ✅ REMOVE TIMEZONE
        df = remove_timezone(df, 'date')
        
        # Filter to our date range
        df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)].copy()
        
        if df.empty:
            print(f"   ⚠️ No earnings in date range {START_DATE} to {END_DATE}")
            return pd.DataFrame()
        
        df = df.sort_values('date', ascending=False).reset_index(drop=True)
        
        print(f"   ✅ Filtered to {len(df)} earnings events in date range")
        print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        print(f"\n   Sample earnings dates:")
        for i, row in df.head(3).iterrows():
            print(f"      {row['date'].date()}")
        
        return df
        
    except Exception as e: 
        print(f"   ❌ Error fetching from Yahoo Finance: {e}")
        return pd.DataFrame()


def get_stock_prices_yahoo(symbol):
    """
    Alternative: Get stock prices from Yahoo Finance (if FMP fails)
    """
    print(f"\n📊 Fetching stock prices from Yahoo Finance for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        df = ticker.history(start=START_DATE, end=END_DATE)
        
        if df.empty:
            print(f"   ❌ No price data")
            return pd.DataFrame()
        
        # Reset index (date is index)
        df = df.reset_index()
        
        # Rename columns to match FMP format
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        df['symbol'] = symbol
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"   ✅ Retrieved {len(df)} price records from Yahoo Finance")
        print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        return df
        
    except Exception as e:
        print(f"   ❌ Error:  {e}")
        return pd.DataFrame()


def get_company_info_yahoo(symbol):
    """Get company info from Yahoo Finance"""
    print(f"\n🏢 Fetching company info from Yahoo Finance for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        print(f"   ✅ {info.get('longName', symbol)}")
        
        return {
            'symbol': symbol,
            'name':  info.get('longName'),
            'exchange': info.get('exchange'),
            'currency': info.get('currency'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'marketCap': info.get('marketCap'),
            'price': info.get('currentPrice')
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}


# ============================================================================
# SMART DATA COLLECTION (tries multiple sources)
# ============================================================================

def get_stock_prices(symbol):
    """
    Smart function:  Try FMP first, fallback to Yahoo Finance
    """
    # Try FMP first (shows API skills)
    df = get_stock_prices_fmp(symbol)
    
    if not df.empty:
        return df
    
    # Fallback to Yahoo Finance
    print(f"\n   FMP failed, falling back to Yahoo Finance...")
    return get_stock_prices_yahoo(symbol)


def get_earnings_data(symbol):
    """
    Get earnings from Yahoo Finance (free, reliable, historical)
    """
    return get_earnings_yahoo(symbol)


def get_company_info(symbol):
    """
    Get company info from multiple sources and merge
    - Search Symbol API:  Basic info (5 columns)
    - Quote API: Real-time data (15 columns)
    Total: 20 columns
    """
    print(f"\n🏢 Fetching company info for {symbol}...")
    
    # Step 1: Get basic info from Search Symbol API
    info_search = get_company_info_fmp(symbol)
    
    if info_search:
        print(f"   ✅ Search API:  {len(info_search)} fields")
    else:
        print(f"   ⚠️ Search API failed")
        info_search = {}
    
    # Step 2: Get real-time quote data from Quote API
    print(f"\n💹 Fetching quote data for {symbol}...")
    info_quote = get_current_quote(symbol)  # �� ADD THIS CALL!
    
    if info_quote:
        print(f"   ✅ Quote API: {len(info_quote)} fields")
    else:
        print(f"   ⚠️ Quote API failed")
        info_quote = {}
    
    # Step 3: Merge both
    if info_search or info_quote:
        combined = {**info_search, **info_quote}
        print(f"   ✅ Total:  {len(combined)} fields")
        return combined
    else:
        # Fallback to Yahoo Finance if both failed
        print(f"   ⚠️ Both APIs failed, trying Yahoo Finance...")
        return get_company_info_yahoo(symbol)
    

# ============================================================================
# ANALYSIS 
# ============================================================================

def calculate_earnings_metrics(symbol, prices_df, earnings_df):
    """Calculate metrics for earnings events - WITH AGGRESSIVE TIMEZONE FIX"""
    print(f"\n🔬 Calculating metrics for {symbol}...")
    
    if earnings_df.empty or prices_df.empty:
        print("   ❌ No data to analyze")
        return None
    
    # AGGRESSIVE FIX:  Ensure both dataframes have timezone-naive dates
    # Fix prices_df
    if 'date' in prices_df. columns:
        prices_df = prices_df.copy()
        prices_df['date'] = pd.to_datetime(prices_df['date']).dt.tz_localize(None)
    
    # Fix earnings_df  
    if 'date' in earnings_df.columns:
        earnings_df = earnings_df. copy()
        earnings_df['date'] = pd.to_datetime(earnings_df['date']).dt.tz_localize(None)
    
    print(f"   ✅ Timezone info removed from all dates")
    print(f"   Prices date dtype: {prices_df['date']. dtype}")
    print(f"   Earnings date dtype: {earnings_df['date'].dtype}")
    
    # Try multiple earnings events
    for i in range(min(len(earnings_df), 5)):
        earnings_row = earnings_df.iloc[i]
        
        # CRITICAL FIX: Convert earnings_date to timezone-naive Timestamp
        earnings_date_raw = earnings_row['date']
        
        # Force conversion to timezone-naive
        if isinstance(earnings_date_raw, pd.Timestamp):
            if earnings_date_raw. tz is not None:
                earnings_date = earnings_date_raw.tz_localize(None)
            else:
                earnings_date = earnings_date_raw
        else:
            earnings_date = pd. Timestamp(earnings_date_raw).tz_localize(None)
        
        print(f"\n   Trying earnings #{i+1} on:  {earnings_date. date()}")
        print(f"   Earnings date type: {type(earnings_date)}, tz: {earnings_date. tz}")
        
        try:
            # comparison
            prices_before = prices_df[prices_df['date'] < earnings_date]. copy()
            prices_after = prices_df[prices_df['date'] >= earnings_date]. copy()
            
            print(f"      Before:   {len(prices_before)} days, After: {len(prices_after)} days")
            
            if len(prices_before) >= PRE_EARNINGS_DAYS + 1 and len(prices_after) >= POST_EARNINGS_DAYS: 
                print(f"      ✅ Sufficient data!")
                
                # Calculate returns
                pre_window = prices_before.tail(PRE_EARNINGS_DAYS + 1)
                post_window = prices_after.head(POST_EARNINGS_DAYS + 1)
                
                pre_return = ((pre_window.iloc[-1]['close'] - pre_window.iloc[0]['close']) / pre_window.iloc[0]['close']) * 100
                post_return = ((post_window.iloc[-1]['close'] - post_window.iloc[0]['close']) / post_window.iloc[0]['close']) * 100
                
                immediate_return = None
                if len(post_window) > 1:
                    immediate_return = ((post_window.iloc[1]['close'] - post_window.iloc[0]['close']) / post_window.iloc[0]['close']) * 100
                
                print(f"\n   📈 Results:")
                print(f"      Pre-earnings return: {pre_return:+.2f}%")
                print(f"      Post-earnings return: {post_return:+.2f}%")
                if immediate_return: 
                    print(f"      Immediate reaction: {immediate_return:+.2f}%")
                
                # EPS data
                eps_actual = earnings_row. get('eps') or earnings_row.get('Reported EPS')
                eps_estimated = earnings_row.get('epsEstimated') or earnings_row.get('Estimate')
                
                eps_surprise_pct = None
                eps_category = "Unknown"
                
                if pd.notna(eps_actual) and pd.notna(eps_estimated) and eps_estimated != 0:
                    eps_surprise_pct = ((eps_actual - eps_estimated) / abs(eps_estimated)) * 100
                    
                    if eps_surprise_pct > BEAT_THRESHOLD:
                        eps_category = "Beat"
                    elif eps_surprise_pct < MISS_THRESHOLD:
                        eps_category = "Miss"
                    else:
                        eps_category = "In-Line"
                    
                    print(f"      EPS Surprise: {eps_surprise_pct: +.1f}% ({eps_category})")
                
                return {
                    'symbol': symbol,
                    'earnings_date': earnings_date,
                    'pre_return_pct': pre_return,
                    'post_return_pct': post_return,
                    'immediate_return_pct': immediate_return,
                    'eps_surprise_pct': eps_surprise_pct,
                    'eps_category': eps_category,
                    'pre_start_price': pre_window.iloc[0]['close'],
                    'earnings_price': pre_window.iloc[-1]['close'],
                    'post_end_price': post_window.iloc[-1]['close']
                }
                
        except TypeError as e:
            print(f"      ❌ Timezone comparison error: {e}")
            print(f"      Debug - prices_df['date'] sample: {prices_df['date']. iloc[0]}")
            print(f"      Debug - earnings_date:  {earnings_date}")
            continue
        except Exception as e:
            print(f"      ❌ Error:  {e}")
            continue
    
    print(f"   ❌ No earnings with sufficient surrounding data")
    return None

def save_data(prices_df, earnings_df, company_info, metrics):
    """Save all data"""
    print(f"\n💾 Saving data to CSV files...")
    
    if not prices_df.empty:
        prices_df.to_csv(STOCK_PRICES_RAW, index=False)
        print(f"   ✅ Stock prices:  {STOCK_PRICES_RAW}")
    
    if not earnings_df.empty:
        earnings_df.to_csv(EARNINGS_DATES_RAW, index=False)
        print(f"   ✅ Earnings dates: {EARNINGS_DATES_RAW}")
    
    if company_info:
        pd.DataFrame([company_info]).to_csv(COMPANY_INFO_RAW, index=False)
        print(f"   ✅ Company info: {COMPANY_INFO_RAW}")
    
    if metrics:
        pd.DataFrame([metrics]).to_csv(os.path.join(PROCESSED_DATA_DIR, 'test_metrics.csv'), index=False)
        print(f"   ✅ Metrics: test_metrics.csv")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*80)
    print("DAY 1: HYBRID APPROACH (FMP APIs + YAHOO FINANCE)")
    print("="*80)
    print("\nStrategy:")
    print("  - Stock Prices: FMP API (primary), Yahoo Finance (fallback)")
    print("  - Earnings Data: Yahoo Finance (free historical data)")
    print("  - Company Info: FMP API (primary), Yahoo Finance (fallback)")
    print("="*80)
    
    symbol = 'AAPL'
    
    
    # Get data from best source for each type
    prices_df = get_stock_prices(symbol)
    time.sleep(0.5)
    
    if prices_df.empty:
        print("\n❌ Failed to get stock prices")
        return
    
    earnings_df = get_earnings_data(symbol)
    time.sleep(0.5)
    
    if earnings_df. empty:
        print("\n❌ Failed to get earnings data")
        return
    
    company_info = get_company_info(symbol)
    time.sleep(0.5)
    
    # Calculate metrics
    metrics = calculate_earnings_metrics(symbol, prices_df, earnings_df)
    
    # Save everything
    save_data(prices_df, earnings_df, company_info, metrics)
    
    # Summary
    print("\n" + "="*80)
    print("✅ DAY 1 COMPLETE!")
    print("="*80)
    print(f"\n📊 Data Collected:")
    print(f"   Stock prices: {len(prices_df)} records")
    print(f"   Earnings events: {len(earnings_df)} events")
    print(f"   Metrics calculated: {'Yes' if metrics else 'No'}")
    
    if metrics:
        print(f"\n📈 Sample Analysis:")
        print(f"   Date:  {metrics['earnings_date'].date()}")
        print(f"   Pre-return: {metrics['pre_return_pct']:+.2f}%")
        print(f"   Post-return: {metrics['post_return_pct']:+.2f}%")
        if metrics['eps_surprise_pct']:
            print(f"   EPS:  {metrics['eps_surprise_pct']:+.1f}% ({metrics['eps_category']})")
    
    print("\n" + "="*80)
    print("Next:  Review data, then move to Day 2 (6 companies + SQL)")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()