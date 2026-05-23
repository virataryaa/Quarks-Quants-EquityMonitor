import pandas as pd

parquet_path = r"C:\Users\virat.arya\Downloads\pranav's\Database\nifty50_ohlc.parquet"
df = pd.read_parquet(parquet_path)

print("=" * 80)
print("PARQUET FILE INFO")
print("=" * 80)
print(f"\nShape: {df.shape} (rows, columns)")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nDate Range: {df['Date'].min()} to {df['Date'].max()}")
print(f"\nEquities ({len(df['Equity'].unique())}): {sorted(df['Equity'].unique().tolist())}")
print(f"\nIndustries ({len(df['Industry'].unique())}): {sorted(df['Industry'].unique().tolist())}")

print("\n" + "=" * 80)
print("FIRST 15 ROWS")
print("=" * 80)
print(df.head(15))

print("\n" + "=" * 80)
print("SAMPLE: HDFCBANK (First 10 rows)")
print("=" * 80)
print(df[df['Equity'] == 'HDFCBANK'].head(10))

print("\n" + "=" * 80)
print("SAMPLE: RELIANCE (Last 10 rows)")
print("=" * 80)
print(df[df['Equity'] == 'RELIANCE'].tail(10))

print("\n" + "=" * 80)
print("SUMMARY STATS")
print("=" * 80)
print(f"Total rows: {len(df):,}")
print(f"Rows per equity (mean): {len(df) / len(df['Equity'].unique()):.0f}")
print(f"\nPrice columns summary:")
print(df[['Open', 'High', 'Low', 'Close']].describe())
