# Quarks Quants Equity Monitor

A comprehensive Streamlit dashboard for analyzing NIFTY 50 equity performance, correlations, and returns distribution.

## Features

- **Indexed Performance**: Track indexed returns of individual equities and industries from a selected start date
- **Correlation Analysis**: View correlation matrix with NIFTY 50 and SENSEX indices
- **Log Returns Distribution**: Analyze frequency distributions of daily log returns at equity and industry levels
- **Interactive Filters**: Date range selector, industry and equity multiselect with Select All options

## Project Structure

```
Quarks-Quants-EquityMonitor/
├── Dashboard/
│   └── app.py           # Main Streamlit application
├── Ingesstion/
│   └── reliance_ohlc.py # Data ingestion script for NIFTY 50 from yfinance
├── Database/
│   └── nifty50_ohlc.parquet  # Combined OHLC data (all 50 stocks, full history)
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/virataryaa/Quarks-Quants-EquityMonitor.git
cd Quarks-Quants-EquityMonitor
```

2. Install dependencies:
```bash
pip install streamlit plotly pandas numpy scipy yfinance
```

## Deployment

### Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with GitHub
3. Click "New app" and select:
   - Repository: `virataryaa/Quarks-Quants-EquityMonitor`
   - Branch: `main`
   - Main file path: `Downloads/pranav's/Dashboard/app.py`
4. Click Deploy

The app will automatically:
- Install dependencies from `requirements.txt`
- Load the parquet file from GitHub (if not available locally)
- Run on Streamlit Cloud infrastructure

## Usage

### Data Ingestion

To fetch fresh NIFTY 50 data from yfinance:
```bash
cd Ingesstion
python reliance_ohlc.py
```

This will generate `nifty50_ohlc.parquet` in the Database folder with columns:
- Date
- Equity
- Industry
- Open, High, Low, Close

### Running the Dashboard

```bash
cd Dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## Dashboard Tabs

1. **Indexed Performance**: Indexed line charts (base=100) for equities and industries
2. **Correlation Analysis**: Heatmap showing correlations between equities and with market indices
3. **Log Returns Distribution**: Histograms and summary statistics of daily log returns

## Data

- **Source**: Yahoo Finance (yfinance)
- **Symbols**: All 50 NIFTY 50 constituents with NSE suffixes (.NS)
- **History**: Full available history from ~1996 onwards
- **Industries**: 13 major industry sectors

## Author

Virat Arya (viratarya30@gmail.com)
