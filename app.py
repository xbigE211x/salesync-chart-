import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sales Volume Tracker", layout="wide")

# --- 1. DIRECT DATA PULL ---
# We use the direct export URL for your specific sheet
sheet_id = "1PpjlhvOPNqBa27w_wNcnmr8PTeqW24SBkZMS0RZZJuM"
sheet_name = "Sheet1" # Assuming data is on the first tab
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

try:
    data = pd.read_csv(url)
except Exception as e:
    st.error(f"Could not load data. Error: {e}")
    st.stop()

# --- 2. DATA CLEANING ---
# We verify the columns exist. We look for 'Timestamp' and 'Select Campaign/Provider'
# We strip whitespace from headers just in case
data.columns = data.columns.str.strip()

if 'Timestamp' not in data.columns or 'Select Campaign/Provider' not in data.columns:
    st.error(f"Column names not found. Found columns: {data.columns.tolist()}")
    st.stop()

# Convert Timestamp column to datetime objects
data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')

# Create a clean 'Date' column for grouping
data['Date'] = data['Timestamp'].dt.date

# Sort by date
data = data.sort_values(by="Date")

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("Filter Options")

# Get unique campaigns
campaign_list = data['Select Campaign/Provider'].dropna().unique().tolist()

selected_campaigns = st.sidebar.multiselect(
    "Select Campaign/Provider", 
    options=campaign_list, 
    default=campaign_list
)

# --- 4. FILTERING ---
if selected_campaigns:
    filtered_data = data[data['Select Campaign/Provider'].isin(selected_campaigns)]
else:
    filtered_data = data

# --- 5. AGGREGATION ---
# Count rows per day
daily_volume = filtered_data.groupby('Date')['Timestamp'].count().reset_index()
daily_volume.rename(columns={'Timestamp': 'Volume'}, inplace=True)

# --- 6. KPI METRICS ---
total_volume = daily_volume['Volume'].sum()
active_days = daily_volume['Date'].nunique()
avg_daily = total_volume / active_days if active_days > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales Volume", f"{total_volume}")
col2.metric("Active Sales Days", f"{active_days}")
col3.metric("Avg. Sales / Day", f"{avg_daily:.1f}")

# --- 7. CHART ---
st.subheader("Daily Sales Volume")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=daily_volume['Date'], 
    y=daily_volume['Volume'],
    mode='lines+markers',
    name='Sales Volume',
    line=dict(color='#00CC96', width=3),
    fill='tozeroy'
))

fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(step="all", label="All Time")
            ]),
            bgcolor="#2E2E2E",
        ),
        rangeslider=dict(visible=True),
        type="date"
    ),
    yaxis=dict(title="Volume"),
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig, use_container_width=True)
