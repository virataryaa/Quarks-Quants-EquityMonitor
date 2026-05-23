import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import yfinance as yf
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="NIFTY 50 Dashboard", layout="wide", initial_sidebar_state="expanded")

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    parquet_path = r"C:\Users\virat.arya\Downloads\pranav's\Database\nifty50_ohlc.parquet"
    df = pd.read_parquet(parquet_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

@st.cache_data
def fetch_indices():
    indices = {}
    try:
        nifty = yf.download("^NSEI", progress=False)
        nifty['Equity'] = 'NIFTY 50'
        indices['NIFTY 50'] = nifty[['Close']].reset_index().rename(columns={'Date': 'Date', 'Close': 'Close'})

        sensex = yf.download("^BSESN", progress=False)
        sensex['Equity'] = 'SENSEX'
        indices['SENSEX'] = sensex[['Close']].reset_index().rename(columns={'Date': 'Date', 'Close': 'Close'})
    except:
        st.warning("Could not fetch indices. They will be excluded from correlation analysis.")
    return indices

df = load_data()
indices = fetch_indices()

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================
st.sidebar.header("Filters")

# Date range
min_date = df['Date'].min()
max_date = df['Date'].max()
start_date = st.sidebar.date_input("Start Date", value=pd.Timestamp(2015, 1, 1), min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

# Industry filter
industries = sorted(df['Industry'].unique())
col_ind1, col_ind2 = st.sidebar.columns([0.8, 0.2])
with col_ind1:
    selected_industries = st.multiselect("Industries", industries, default=industries)
with col_ind2:
    if st.button("All", key="ind_all"):
        selected_industries = industries
        st.rerun()

# Equity filter
all_equities = sorted(df['Equity'].unique())
equities = sorted(df[df['Industry'].isin(selected_industries)]['Equity'].unique())
col_eq1, col_eq2 = st.sidebar.columns([0.8, 0.2])
with col_eq1:
    selected_equities = st.multiselect("Equities", equities, default=equities[:10] if len(equities) > 10 else equities)
with col_eq2:
    if st.button("All", key="eq_all"):
        selected_equities = equities
        st.rerun()

# Filter data
filtered_df = df[
    (df['Date'] >= pd.Timestamp(start_date)) &
    (df['Date'] <= pd.Timestamp(end_date)) &
    (df['Equity'].isin(selected_equities))
].copy()

st.sidebar.info(f"Showing {len(selected_equities)} equities from {len(selected_industries)} industries\nDate range: {start_date} to {end_date}")

# ============================================================================
# MAIN TABS
# ============================================================================
tab1, tab2, tab3 = st.tabs(["Indexed Performance", "Correlation Analysis", "Log Returns Distribution"])

# ============================================================================
# TAB 1: INDEXED PERFORMANCE
# ============================================================================
with tab1:
    st.subheader("Indexed Performance (Base = 100)")

    col1, col2 = st.columns(2)

    with col1:
        # Equity Performance
        st.write("Equity Performance")

        indexed_data = []
        for equity in selected_equities:
            equity_df = filtered_df[filtered_df['Equity'] == equity].sort_values('Date').copy()
            if len(equity_df) > 0:
                first_close = equity_df['Close'].iloc[0]
                equity_df['Indexed'] = (equity_df['Close'] / first_close) * 100
                indexed_data.append(equity_df[['Date', 'Equity', 'Indexed']])

        if indexed_data:
            indexed_df = pd.concat(indexed_data)
            fig_equity = px.line(indexed_df, x='Date', y='Indexed', color='Equity',
                                title='Indexed Performance by Equity', template='plotly_dark')
            fig_equity.update_layout(
                hovermode='x unified',
                height=500,
                hoverlabel=dict(namelength=-1)
            )
            fig_equity.update_traces(
                hovertemplate='<b>%{customdata}</b><br>Date: %{x|%Y-%m-%d}<br>Indexed: %{y:.2f}<extra></extra>',
                customdata=indexed_df['Equity']
            )
            st.plotly_chart(fig_equity, use_container_width=True)
        else:
            st.warning("No data available for selected equities")

    with col2:
        # Industry Performance
        st.write("Industry Performance")

        industry_data = []
        for industry in selected_industries:
            industry_df = filtered_df[filtered_df['Industry'] == industry].sort_values('Date').copy()
            if len(industry_df) > 0:
                # Average close price per day for the industry
                daily_avg = industry_df.groupby('Date')['Close'].mean()
                first_close = daily_avg.iloc[0]
                indexed = (daily_avg / first_close) * 100
                for date, val in indexed.items():
                    industry_data.append({'Date': date, 'Industry': industry, 'Indexed': val})

        if industry_data:
            industry_indexed = pd.DataFrame(industry_data)
            fig_industry = px.line(industry_indexed, x='Date', y='Indexed', color='Industry',
                                  title='Indexed Performance by Industry', template='plotly_dark')
            fig_industry.update_layout(
                hovermode='x unified',
                height=500,
                hoverlabel=dict(namelength=-1)
            )
            fig_industry.update_traces(
                hovertemplate='<b>%{customdata}</b><br>Date: %{x|%Y-%m-%d}<br>Indexed: %{y:.2f}<extra></extra>',
                customdata=industry_indexed['Industry']
            )
            st.plotly_chart(fig_industry, use_container_width=True)
        else:
            st.warning("No data available for selected industries")

# ============================================================================
# TAB 2: CORRELATION ANALYSIS
# ============================================================================
with tab2:
    st.subheader("Correlation Matrix with Indices")

    # Prepare correlation data
    corr_data = filtered_df[['Date', 'Equity', 'Close']].pivot(index='Date', columns='Equity', values='Close')

    # Add indices if available
    if indices:
        for idx_name, idx_df in indices.items():
            idx_df['Date'] = pd.to_datetime(idx_df['Date'])
            idx_df = idx_df[(idx_df['Date'] >= pd.Timestamp(start_date)) &
                           (idx_df['Date'] <= pd.Timestamp(end_date))].set_index('Date')
            if len(idx_df) > 0:
                corr_data[idx_name] = idx_df['Close']

    corr_data = corr_data.dropna()

    if len(corr_data) > 1:
        # Calculate correlations
        corr_matrix = corr_data.corr()

        # Remove diagonal (set to NaN)
        np.fill_diagonal(corr_matrix.values, np.nan)

        # Create heatmap with masked diagonal
        z_values = corr_matrix.values.copy()
        text_values = np.round(z_values, 2).astype(str)
        text_values[np.isnan(z_values)] = ""

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=z_values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            zmin=-1,
            zmax=1,
            text=text_values,
            texttemplate='%{text}',
            textfont={"size": 8},
            colorbar=dict(title="Correlation"),
            hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        fig_heatmap.update_layout(height=700, title="Correlation Matrix (Daily Closes)", template='plotly_dark')
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Show top correlations with indices
        if indices:
            st.write("Top Correlations with Indices")

            cols = st.columns(len(indices))
            for col_idx, (idx_name, _) in enumerate(indices.items()):
                with cols[col_idx]:
                    if idx_name in corr_matrix.columns:
                        idx_corr = corr_matrix[idx_name].drop(idx_name).sort_values(ascending=False)
                        st.write(f"{idx_name}")
                        st.dataframe(idx_corr.head(10), use_container_width=True)
    else:
        st.warning("Not enough data for correlation analysis")

# ============================================================================
# TAB 3: LOG RETURNS DISTRIBUTION
# ============================================================================
with tab3:
    st.subheader("Frequency Distribution of Daily Log Returns")

    col1, col2 = st.columns(2)

    with col1:
        # Equity Log Returns Distribution
        st.write("Equity Log Returns Distribution")

        equity_returns = []
        for equity in selected_equities:
            equity_df = filtered_df[filtered_df['Equity'] == equity].sort_values('Date').copy()
            if len(equity_df) > 1:
                log_returns = np.log(equity_df['Close'] / equity_df['Close'].shift(1)).dropna()
                for ret in log_returns:
                    equity_returns.append({'Equity': equity, 'Log_Return': ret * 100})

        if equity_returns:
            returns_df = pd.DataFrame(equity_returns)
            fig_equity_dist = px.histogram(returns_df, x='Log_Return', color='Equity',
                                          nbins=50, title='Daily Log Returns by Equity',
                                          template='plotly_dark', barmode='overlay')
            fig_equity_dist.update_layout(xaxis_title="Daily Log Return (%)", yaxis_title="Frequency", height=500)
            fig_equity_dist.update_traces(hovertemplate='<b>%{customdata}</b><br>Return: %{x:.2f}%<br>Count: %{y}<extra></extra>',
                                         customdata=returns_df['Equity'])
            st.plotly_chart(fig_equity_dist, use_container_width=True)
        else:
            st.warning("No data available")

    with col2:
        # Industry Log Returns Distribution
        st.write("Industry Log Returns Distribution")

        industry_returns = []
        for industry in selected_industries:
            industry_df = filtered_df[filtered_df['Industry'] == industry].sort_values('Date').copy()
            if len(industry_df) > 0:
                daily_avg = industry_df.groupby('Date')['Close'].mean().sort_index()
                if len(daily_avg) > 1:
                    log_returns = np.log(daily_avg / daily_avg.shift(1)).dropna()
                    for ret in log_returns:
                        industry_returns.append({'Industry': industry, 'Log_Return': ret * 100})

        if industry_returns:
            ind_returns_df = pd.DataFrame(industry_returns)
            fig_ind_dist = px.histogram(ind_returns_df, x='Log_Return', color='Industry',
                                       nbins=50, title='Daily Log Returns by Industry',
                                       template='plotly_dark', barmode='overlay')
            fig_ind_dist.update_layout(xaxis_title="Daily Log Return (%)", yaxis_title="Frequency", height=500)
            fig_ind_dist.update_traces(hovertemplate='<b>%{customdata}</b><br>Return: %{x:.2f}%<br>Count: %{y}<extra></extra>',
                                      customdata=ind_returns_df['Industry'])
            st.plotly_chart(fig_ind_dist, use_container_width=True)
        else:
            st.warning("No data available")

    # Summary Statistics - Equity
    st.write("Summary Statistics - Equity Level")

    all_returns = []
    for equity in selected_equities:
        equity_df = filtered_df[filtered_df['Equity'] == equity].sort_values('Date').copy()
        if len(equity_df) > 1:
            log_returns = np.log(equity_df['Close'] / equity_df['Close'].shift(1)).dropna() * 100
            all_returns.append({
                'Equity': equity,
                'Mean (%)': log_returns.mean(),
                'Std Dev (%)': log_returns.std(),
                'Skewness': stats.skew(log_returns),
                'Kurtosis': stats.kurtosis(log_returns)
            })

    if all_returns:
        stats_df = pd.DataFrame(all_returns).sort_values('Std Dev (%)', ascending=False)
        st.dataframe(stats_df, use_container_width=True)

    # Summary Statistics - Industry
    st.write("Summary Statistics - Industry Level")

    industry_stats = []
    for industry in selected_industries:
        industry_df = filtered_df[filtered_df['Industry'] == industry].sort_values('Date').copy()
        if len(industry_df) > 0:
            daily_avg = industry_df.groupby('Date')['Close'].mean().sort_index()
            if len(daily_avg) > 1:
                log_returns = np.log(daily_avg / daily_avg.shift(1)).dropna() * 100
                industry_stats.append({
                    'Industry': industry,
                    'Mean (%)': log_returns.mean(),
                    'Std Dev (%)': log_returns.std(),
                    'Skewness': stats.skew(log_returns),
                    'Kurtosis': stats.kurtosis(log_returns)
                })

    if industry_stats:
        ind_stats_df = pd.DataFrame(industry_stats).sort_values('Std Dev (%)', ascending=False)
        st.dataframe(ind_stats_df, use_container_width=True)
