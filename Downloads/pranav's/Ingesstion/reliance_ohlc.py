import yfinance as yf
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT_DIR = Path(r"C:\Users\virat.arya\Downloads\pranav's\Database")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NIFTY50_WITH_INDUSTRY = {
    "ADANIENT.NS": "Infrastructure",
    "ADANIPORTS.NS": "Infrastructure",
    "APOLLOHOSP.NS": "Healthcare",
    "ASIANPAINT.NS": "Consumer Durables",
    "AXISBANK.NS": "Financial Services",
    "BAJAJ-AUTO.NS": "Automobile",
    "BAJFINANCE.NS": "Financial Services",
    "BAJAJFINSV.NS": "Financial Services",
    "BPCL.NS": "Energy",
    "BHARTIARTL.NS": "Telecom",
    "BRITANNIA.NS": "FMCG",
    "CIPLA.NS": "Pharma",
    "COALINDIA.NS": "Energy",
    "DIVISLAB.NS": "Pharma",
    "DRREDDY.NS": "Pharma",
    "EICHERMOT.NS": "Automobile",
    "GRASIM.NS": "Materials",
    "HCLTECH.NS": "IT",
    "HDFCBANK.NS": "Financial Services",
    "HDFCLIFE.NS": "Financial Services",
    "HEROMOTOCO.NS": "Automobile",
    "HINDALCO.NS": "Materials",
    "HINDUNILVR.NS": "FMCG",
    "ICICIBANK.NS": "Financial Services",
    "INDUSINDBK.NS": "Financial Services",
    "INFY.NS": "IT",
    "ITC.NS": "FMCG",
    "JSWSTEEL.NS": "Materials",
    "KOTAKBANK.NS": "Financial Services",
    "LT.NS": "Engineering",
    "M&M.NS": "Automobile",
    "MARUTI.NS": "Automobile",
    "NESTLEIND.NS": "FMCG",
    "NTPC.NS": "Energy",
    "ONGC.NS": "Energy",
    "POWERGRID.NS": "Energy",
    "RELIANCE.NS": "Energy",
    "SBILIFE.NS": "Financial Services",
    "SBIN.NS": "Financial Services",
    "SHRIRAMFIN.NS": "Financial Services",
    "SUNPHARMA.NS": "Pharma",
    "TCS.NS": "IT",
    "TATACONSUM.NS": "FMCG",
    "TATAMOTORS.NS": "Automobile",
    "TATASTEEL.NS": "Materials",
    "TECHM.NS": "IT",
    "TITAN.NS": "Consumer Discretionary",
    "TRENT.NS": "Consumer Discretionary",
    "ULTRACEMCO.NS": "Materials",
    "WIPRO.NS": "IT",
}

def fetch_equity_data(ticker: str, period: str = "max") -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
        df.index.name = "Date"
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df = df[["Open", "High", "Low", "Close"]].dropna()

        if df.empty:
            raise ValueError("empty dataframe")

        df["Equity"] = ticker.replace(".NS", "")
        df["Industry"] = NIFTY50_WITH_INDUSTRY[ticker]
        df = df.reset_index()

        return df
    except Exception as e:
        print(f"  [FAIL] {ticker:20s}  {e}")
        return None

if __name__ == "__main__":
    print(f"Fetching {len(NIFTY50_WITH_INDUSTRY)} Nifty 50 stocks (full history from 2000) in parallel...\n")

    all_data = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_equity_data, ticker): ticker for ticker in NIFTY50_WITH_INDUSTRY.keys()}

        for future in as_completed(futures):
            df = future.result()
            if df is not None:
                ticker = futures[future]
                all_data.append(df)
                print(f"  [OK] {ticker:20s}  {len(df)} rows")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df[["Date", "Equity", "Industry", "Open", "High", "Low", "Close"]]
        combined_df = combined_df.sort_values(["Equity", "Date"]).reset_index(drop=True)

        output_file = OUTPUT_DIR / "nifty50_ohlc.parquet"
        combined_df.to_parquet(output_file)

        print(f"\n✓ Combined parquet saved: {output_file}")
        print(f"  Total rows: {len(combined_df)}")
        print(f"  Date range: {combined_df['Date'].min()} to {combined_df['Date'].max()}")
        print(f"\nFirst few rows:")
        print(combined_df.head(10))
