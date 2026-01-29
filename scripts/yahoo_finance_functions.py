# scripts/yahoo_finance_functions.py
"""
Yahoo Finance data collection functions
No API rate limits - completely free!
"""

import pandas as pd
import yfinance as yf
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import START_DATE, END_DATE


# ============================================================================
# TIMEZONE HELPER
# ============================================================================

def remove_timezone(df, date_column='date'):
    """
    Remove timezone information from datetime column
    Converts tz-aware to tz-naive for comparison
    """
    if date_column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[date_column]):
            # If datetime and has timezone, remove it
            df[date_column] = df[date_column].apply(
                lambda x: x.replace(tzinfo=None) if pd.notna(x) and hasattr(x, 'tzinfo') and x.tzinfo is not None else x
            )
        else:
            # Convert to datetime without timezone
            df[date_column] = pd.to_datetime(df[date_column])
            df[date_column] = df[date_column].apply(
                lambda x: x.replace(tzinfo=None) if pd.notna(x) and hasattr(x, 'tzinfo') and x.tzinfo is not None else x
            )
    
    return df


# ============================================================================
# STOCK PRICES
# ============================================================================

def get_stock_prices_yahoo(symbol):
    """
    Fetch historical stock prices from Yahoo Finance
    Returns:  DataFrame with columns: date, open, high, low, close, volume, symbol
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
        
        # Rename columns to match our schema
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume':  'volume'
        })
        
        # Add symbol column
        df['symbol'] = symbol
        
        # Convert date to datetime and remove timezone
        df['date'] = pd.to_datetime(df['date'])
        df = remove_timezone(df, 'date')
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Keep only columns we need
        columns_to_keep = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        df = df[columns_to_keep]
        
        print(f"   ✅ Retrieved {len(df)} price records")
        print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        return df
        
    except Exception as e:
        print(f"   ❌ Error:  {e}")
        return pd.DataFrame()


# ============================================================================
# EARNINGS DATES
# ============================================================================

def get_earnings_yahoo(symbol):
    """
    Fetch earnings dates and EPS data from Yahoo Finance
    Returns: DataFrame with earnings dates, EPS actual, estimated, and surprise
    """
    print(f"\n📅 Fetching earnings data from Yahoo Finance for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Try to get earnings_dates (most detailed)
        print(f"   Accessing Yahoo Finance earnings calendar...")
        earnings_dates = ticker.earnings_dates
        
        if earnings_dates is None or earnings_dates.empty:
            print(f"   ⚠️ No earnings calendar, trying earnings history...")
            
            # Fallback to earnings history
            earnings_history = ticker.earnings
            
            if earnings_history is not None and not earnings_history.empty:
                df = earnings_history.reset_index()
                df.columns = ['date', 'earnings']
                df['date'] = pd.to_datetime(df['date'])
                df['symbol'] = symbol
                
                print(f"   ✅ Retrieved {len(df)} earnings events from history")
            else:
                print(f"   ❌ No earnings data available")
                return pd.DataFrame()
        else:
            # Got earnings_dates - this is the best source
            df = earnings_dates.reset_index()
            df.columns = ['date'] + list(df.columns[1:])
            df['date'] = pd.to_datetime(df['date'])
            df['symbol'] = symbol
            
            print(f"   ✅ Retrieved {len(df)} earnings events from calendar")
        
        # Remove timezone
        df = remove_timezone(df, 'date')
        
        # Filter to our date range
        df = df[(df['date'] >= START_DATE) & (df['date'] <= END_DATE)].copy()
        
        if df.empty:
            print(f"   ⚠️ No earnings in date range {START_DATE} to {END_DATE}")
            return pd.DataFrame()
        
        # Sort by date (most recent first)
        df = df.sort_values('date', ascending=False).reset_index(drop=True)
        
        print(f"   ✅ Filtered to {len(df)} earnings events in date range")
        print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        
        # Show sample dates
        print(f"\n   Sample earnings dates:")
        for i, row in df.head(3).iterrows():
            print(f"      {row['date'].date()}")
        
        return df
        
    except Exception as e:
        print(f"   ❌ Error fetching from Yahoo Finance: {e}")
        return pd.DataFrame()


# ============================================================================
# COMPANY INFO
# ============================================================================

def get_company_info_yahoo(symbol):
    """
    Get company information from Yahoo Finance
    Returns: Dictionary with company details
    """
    print(f"\n🏢 Fetching company info from Yahoo Finance for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        company_name = info.get('longName') or info.get('shortName') or symbol
        print(f"   ✅ {company_name}")
        
        # Extract relevant fields
        company_data = {
            'symbol': symbol,
            'name': company_name,
            'exchange': info.get('exchange'),
            'currency': info.get('currency'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'marketCap': info.get('marketCap'),
            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'volume': info.get('volume'),
            'averageVolume': info.get('averageVolume'),
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow'),
            'fiftyDayAverage': info.get('fiftyDayAverage'),
            'twoHundredDayAverage': info.get('twoHundredDayAverage'),
            'trailingPE': info.get('trailingPE'),
            'forwardPE': info.get('forwardPE'),
            'dividendYield': info.get('dividendYield'),
            'beta': info.get('beta'),
            'website': info.get('website'),
            'description': info.get('longBusinessSummary', '')[: 500] if info.get('longBusinessSummary') else None  # Limit description length
        }
        
        # Count non-None fields
        fields_count = sum(1 for v in company_data.values() if v is not None)
        print(f"   ✅ Collected {fields_count} fields")
        
        return company_data
        
    except Exception as e:
        print(f"   ❌ Error:  {e}")
        return {}


# ============================================================================
# BATCH COLLECTION
# ============================================================================

def collect_all_data_yahoo(symbols):
    """
    Collect all data for multiple symbols using Yahoo Finance only
    
    Args:
        symbols: List of stock symbols or dict of {symbol: name}
    
    Returns:
        prices_df, earnings_df, companies_df
    """
    print("\n" + "="*80)
    print("COLLECTING DATA FROM YAHOO FINANCE (NO RATE LIMITS! )")
    print("="*80)
    
    # Handle both list and dict input
    if isinstance(symbols, dict):
        symbol_list = list(symbols.keys())
        print(f"\nCompanies to analyze: {', '.join(symbol_list)}")
    else:
        symbol_list = symbols
        print(f"\nSymbols to analyze: {', '.join(symbol_list)}")
    
    print(f"Total:  {len(symbol_list)}")
    print("="*80 + "\n")
    
    all_prices = []
    all_earnings = []
    all_companies = []
    
    for i, symbol in enumerate(symbol_list, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(symbol_list)}] Processing {symbol}")
        print(f"{'='*80}")
        
        # 1. Stock prices
        prices = get_stock_prices_yahoo(symbol)
        if not prices.empty:
            all_prices.append(prices)
            print(f"   ✅ Collected {len(prices)} price records")
        else:
            print(f"   ⚠️ No price data for {symbol}")
        
        # 2. Earnings dates
        earnings = get_earnings_yahoo(symbol)
        if not earnings.empty:
            all_earnings.append(earnings)
            print(f"   ✅ Collected {len(earnings)} earnings events")
        else:
            print(f"   ⚠️ No earnings data for {symbol}")
        
        # 3. Company info
        company = get_company_info_yahoo(symbol)
        if company:
            all_companies.append(company)
            print(f"   ✅ Collected company info")
        else:
            print(f"   ⚠️ No company info for {symbol}")
        
        print(f"\n{'='*80}")
        print(f"✅ Completed {symbol}")
        print(f"{'='*80}\n")
    
    # Combine all data
    print("\n" + "="*80)
    print("COMBINING ALL DATA")
    print("="*80)
    
    prices_df = pd.concat(all_prices, ignore_index=True) if all_prices else pd.DataFrame()
    earnings_df = pd.concat(all_earnings, ignore_index=True) if all_earnings else pd.DataFrame()
    companies_df = pd.DataFrame(all_companies) if all_companies else pd.DataFrame()
    
    print(f"\n📊 Combined Results:")
    print(f"   Stock prices: {len(prices_df):,} records across {prices_df['symbol'].nunique() if not prices_df.empty else 0} companies")
    print(f"   Earnings events: {len(earnings_df):,} events across {earnings_df['symbol'].nunique() if not earnings_df.empty else 0} companies")
    print(f"   Company info: {len(companies_df)} companies")
    
    if not companies_df.empty:
        print(f"   Company fields: {len(companies_df.columns)} columns")
    
    return prices_df, earnings_df, companies_df


# ============================================================================
# TEST FUNCTION
# ============================================================================

if __name__ == "__main__": 
    """Test the Yahoo Finance functions"""
    
    print("Testing Yahoo Finance functions.. .\n")
    
    test_symbol = 'AAPL'
    
    # Test each function
    prices = get_stock_prices_yahoo(test_symbol)
    print(f"\nPrices shape: {prices.shape}")
    
    earnings = get_earnings_yahoo(test_symbol)
    print(f"\nEarnings shape: {earnings.shape}")
    
    company = get_company_info_yahoo(test_symbol)
    print(f"\nCompany fields: {len(company)}")
    
    print("\n✅ All tests complete!")