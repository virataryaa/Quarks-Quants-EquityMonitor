# Database

This folder contains the NIFTY 50 OHLC data in parquet format.

## Generating the Data

To generate `nifty50_ohlc.parquet`, run the ingestion script:

```bash
cd ../Ingesstion
python reliance_ohlc.py
```

This will download NIFTY 50 data from Yahoo Finance and save it as `nifty50_ohlc.parquet` in this directory.

### Data Structure

The parquet file contains:
- **Rows**: ~309K (all trading days for 49 equities from 1996-2026)
- **Columns**: Date, Equity, Industry, Open, High, Low, Close
- **Industries**: 13 sectors (Energy, Financial Services, IT, Pharma, Materials, FMCG, etc.)

### File Size

The parquet is not committed to GitHub to keep the repo lightweight. Generate it locally on first setup.
