# scripts/day3_analysis.py
"""
Day 3: Analytical Exploration
Generate insights, statistics, and visualizations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import DATABASE_PATH, PROCESSED_DATA_DIR

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def connect_db():
    """Connect to database"""
    return sqlite3.connect(DATABASE_PATH)


def load_data():
    """Load all analysis data"""
    conn = connect_db()
    
    companies = pd.read_sql("SELECT * FROM companies", conn)
    prices = pd.read_sql("SELECT * FROM stock_prices", conn)
    earnings = pd.read_sql("SELECT * FROM earnings_dates", conn)
    analysis = pd.read_sql("SELECT * FROM earnings_analysis", conn)
    
    conn.close()
    
    return companies, prices, earnings, analysis


def print_summary_statistics(analysis):
    """Print overall summary statistics"""
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\n📊 Overall Metrics:")
    print(f"   Total companies analyzed: {analysis['symbol'].nunique()}")
    print(f"   Total earnings events: {len(analysis)}")
    print(f"   Average post-earnings return: {analysis['post_return_pct'].mean():.2f}%")
    print(f"   Average immediate return: {analysis['immediate_return_pct']. mean():.2f}%")
    print(f"   Win rate (positive returns): {(analysis['post_return_pct'] > 0).sum() / len(analysis) * 100:.1f}%")
    print(f"   Best reaction: {analysis['post_return_pct'].max():.2f}%")
    print(f"   Worst reaction: {analysis['post_return_pct'].min():.2f}%")
    print(f"   Standard deviation: {analysis['post_return_pct'].std():.2f}%")


def analyze_by_company(analysis):
    """Analyze performance by company"""
    print("\n" + "="*80)
    print("PERFORMANCE BY COMPANY")
    print("="*80)
    
    company_stats = analysis.groupby('symbol').agg({
        'post_return_pct': ['count', 'mean', 'std', 'min', 'max'],
        'immediate_return_pct': 'mean',
        'eps_surprise_pct': 'mean'
    }).round(2)
    
    company_stats.columns = ['Count', 'Avg Return', 'Std Dev', 'Min', 'Max', 'Avg Immediate', 'Avg EPS Surprise']
    
    # Add win rate
    company_stats['Win Rate %'] = analysis. groupby('symbol').apply(
        lambda x: (x['post_return_pct'] > 0).sum() / len(x) * 100
    ).round(1)
    
    company_stats = company_stats.sort_values('Avg Return', ascending=False)
    
    print("\n", company_stats)
    
    return company_stats


def analyze_eps_impact(analysis):
    """Analyze impact of EPS surprises"""
    print("\n" + "="*80)
    print("EPS SURPRISE IMPACT")
    print("="*80)
    
    eps_stats = analysis[analysis['eps_category'] != 'Unknown'].groupby('eps_category').agg({
        'post_return_pct': ['count', 'mean', 'std'],
        'immediate_return_pct': 'mean'
    }).round(2)
    
    eps_stats.columns = ['Count', 'Avg Return', 'Std Dev', 'Avg Immediate']
    
    # Add win rate
    eps_stats['Win Rate %'] = analysis[analysis['eps_category'] != 'Unknown'].groupby('eps_category').apply(
        lambda x: (x['post_return_pct'] > 0).sum() / len(x) * 100
    ).round(1)
    
    print("\n", eps_stats)
    
    # Sell the news analysis
    sell_news = analysis[(analysis['eps_surprise_pct'] > 0) & (analysis['post_return_pct'] < 0)]
    print(f"\n📉 'Sell the News' Phenomenon:")
    print(f"   Earnings that beat but stock dropped: {len(sell_news)} ({len(sell_news)/len(analysis)*100:.1f}%)")
    
    return eps_stats


def find_insights(analysis):
    """Find interesting insights"""
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    # 1. Best performer
    best = analysis.loc[analysis['post_return_pct'].idxmax()]
    print(f"\n🏆 Best Earnings Reaction:")
    print(f"   {best['symbol']} on {best['earnings_date']}:  +{best['post_return_pct']:.2f}%")
    print(f"   EPS:  {best['eps_category']}")
    
    # 2. Worst performer
    worst = analysis.loc[analysis['post_return_pct'].idxmin()]
    print(f"\n📉 Worst Earnings Reaction:")
    print(f"   {worst['symbol']} on {worst['earnings_date']}: {worst['post_return_pct']:.2f}%")
    print(f"   EPS: {worst['eps_category']}")
    
    # 3. Most consistent
    volatility = analysis.groupby('symbol')['post_return_pct']. std().sort_values()
    print(f"\n🎯 Most Consistent (lowest volatility):")
    print(f"   {volatility.index[0]}: {volatility.iloc[0]:.2f}% std dev")
    
    # 4. Most volatile
    print(f"\n🎢 Most Volatile (highest volatility):")
    print(f"   {volatility. index[-1]}: {volatility.iloc[-1]:.2f}% std dev")
    
    # 5. EPS beats that dropped
    beats_dropped = analysis[(analysis['eps_category'] == 'Beat') & (analysis['post_return_pct'] < -2)]
    print(f"\n⚠️  Earnings Beats that Dropped >2%:  {len(beats_dropped)}")
    if len(beats_dropped) > 0:
        print("   Examples:")
        for _, row in beats_dropped.head(3).iterrows():
            print(f"   - {row['symbol']} on {row['earnings_date']}: {row['post_return_pct']:.2f}%")


def create_visualizations(analysis, company_stats):
    """Create and save visualizations"""
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    viz_dir = os.path.join(PROCESSED_DATA_DIR, 'visualizations')
    os.makedirs(viz_dir, exist_ok=True)
    
    # 1. Returns distribution
    plt.figure(figsize=(12, 6))
    plt.hist(analysis['post_return_pct'], bins=30, edgecolor='black', alpha=0.7)
    plt.axvline(0, color='red', linestyle='--', label='Break-even')
    plt.axvline(analysis['post_return_pct']. mean(), color='green', linestyle='--', label=f'Mean: {analysis["post_return_pct"].mean():.2f}%')
    plt.xlabel('Post-Earnings Return (%)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Post-Earnings Returns')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(viz_dir, '01_returns_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved:  01_returns_distribution.png")
    plt.close()
    
    # 2. Company performance
    plt.figure(figsize=(12, 6))
    company_stats['Avg Return'].sort_values().plot(kind='barh', color='steelblue')
    plt.axvline(0, color='red', linestyle='--', alpha=0.5)
    plt.xlabel('Average Post-Earnings Return (%)')
    plt.title('Average Post-Earnings Return by Company')
    plt.grid(alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, '02_company_performance.png'), dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: 02_company_performance.png")
    plt.close()
    
    # 3. EPS Impact
    eps_data = analysis[analysis['eps_category'] != 'Unknown']. groupby('eps_category')['post_return_pct']. mean().sort_values()
    plt.figure(figsize=(10, 6))
    eps_data.plot(kind='bar', color=['red', 'gray', 'green'])
    plt.axhline(0, color='black', linestyle='--', alpha=0.5)
    plt.xlabel('EPS Category')
    plt.ylabel('Average Post-Earnings Return (%)')
    plt.title('Stock Performance by EPS Result')
    plt.xticks(rotation=0)
    plt.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path. join(viz_dir, '03_eps_impact.png'), dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved:  03_eps_impact.png")
    plt.close()
    
    # 4. Scatter:  EPS Surprise vs Stock Return
    filtered = analysis[analysis['eps_surprise_pct']. notna()]
    plt.figure(figsize=(12, 6))
    for symbol in filtered['symbol'].unique():
        data = filtered[filtered['symbol'] == symbol]
        plt.scatter(data['eps_surprise_pct'], data['post_return_pct'], label=symbol, alpha=0.6, s=100)
    plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(0, color='gray', linestyle='--', alpha=0.5)
    plt.xlabel('EPS Surprise (%)')
    plt.ylabel('Post-Earnings Return (%)')
    plt.title('EPS Surprise vs Stock Performance')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, '04_eps_vs_return.png'), dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: 04_eps_vs_return.png")
    plt.close()
    
    print(f"\n📁 Visualizations saved to: {viz_dir}")


def export_summary_report(analysis, company_stats, eps_stats):
    """Export summary report"""
    print("\n" + "="*80)
    print("EXPORTING SUMMARY REPORT")
    print("="*80)
    
    report_path = os.path.join(PROCESSED_DATA_DIR, 'analysis_summary.txt')
    
    with open(report_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("EARNINGS STOCK ANALYSIS - SUMMARY REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write("OVERALL STATISTICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Total companies:  {analysis['symbol'].nunique()}\n")
        f.write(f"Total earnings events: {len(analysis)}\n")
        f.write(f"Average return: {analysis['post_return_pct'].mean():.2f}%\n")
        f.write(f"Win rate:  {(analysis['post_return_pct'] > 0).sum() / len(analysis) * 100:.1f}%\n\n")
        
        f. write("COMPANY PERFORMANCE\n")
        f.write("-"*80 + "\n")
        f.write(company_stats.to_string())
        f.write("\n\n")
        
        f.write("EPS IMPACT\n")
        f.write("-"*80 + "\n")
        f.write(eps_stats.to_string())
        f.write("\n\n")
    
    print(f"   ✅ Report saved to: {report_path}")


def main():
    """Main analysis execution"""
    print("\n" + "="*80)
    print("DAY 3: DATA ANALYSIS & INSIGHTS")
    print("="*80)
    
    # Load data
    print("\n📂 Loading data from database...")
    companies, prices, earnings, analysis = load_data()
    print(f"   ✅ Loaded:  {len(analysis)} analyzed earnings events")
    
    # Run analyses
    print_summary_statistics(analysis)
    company_stats = analyze_by_company(analysis)
    eps_stats = analyze_eps_impact(analysis)
    find_insights(analysis)
    
    # Create visualizations
    create_visualizations(analysis, company_stats)
    
    # Export report
    export_summary_report(analysis, company_stats, eps_stats)
    
    print("\n" + "="*80)
    print("✅ DAY 3 ANALYSIS COMPLETE!")
    print("="*80)
    print("\nNext:  Create Power BI dashboard using the CSV files!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()