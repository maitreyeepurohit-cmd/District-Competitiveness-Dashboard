import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
st.set_page_config(layout="wide", page_title="Dairy RCA Dashboard")
st.title("🧀 District Competitiveness Dashboard: Dairy Sector (RCA-based)")

# Upload CSV
df = pd.read_csv("lovable.csv")

# Identify time series columns
time_cols = df.columns[13:]
df[time_cols] = df[time_cols].replace("-", pd.NA).astype(float)

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")
    states = df["State"].dropna().unique()
    selected_state = st.selectbox("Select State", sorted(states))

    districts = df[df["State"] == selected_state]["District"].dropna().unique()
    selected_district = st.selectbox("Select District", sorted(districts))

    rca_threshold = st.slider("Minimum RCA Threshold", 0.0, 10.0, 4.0, step=0.1)

# Filter the data
filtered_df = df[(df["State"] == selected_state) & (df["District"] == selected_district)]

# Show district details
if not filtered_df.empty:
    district_name = filtered_df["District"].values[0]
    sub_sector = filtered_df["Sub-Sector"].values[0]
    activity = filtered_df["Occupation/Activity"].values[0]
    latest_date = time_cols[-1]
    latest_rca = filtered_df[latest_date].values[0]

    st.subheader(f"📍 Overview: {district_name}, {selected_state}")
    st.markdown(f"- **Sub-Sector**: {sub_sector}")
    st.markdown(f"- **Occupation/Activity**: {activity}")
    st.metric("📊 Latest RCA Value", f"{latest_rca:.2f}", help="Latest RCA index value as of most recent date")

    # RCA Trend chart
    rca_series = filtered_df[time_cols].T.reset_index()
    rca_series.columns = ["Date", "RCA"]
    rca_series["Date"] = pd.to_datetime(rca_series["Date"], errors="coerce", format="%d-%m-%Y")
    rca_series = rca_series.dropna()

    fig = px.line(rca_series, x="Date", y="RCA", title=f"📈 RCA Trend Over Time: {district_name}",
                  markers=True, template="plotly_white")
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

# Top RCA districts in the latest quarter
st.markdown("## 🏆 Top Performing Dairy Districts (Based on Latest RCA)")
top_df = df[["State", "District", latest_date]].dropna()
top_df = top_df[top_df[latest_date] >= rca_threshold]
top_df_sorted = top_df.sort_values(by=latest_date, ascending=False).reset_index(drop=True)

st.dataframe(top_df_sorted, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**RCA Definition:**  
> RCA = (Dairy Credit in District / Total Credit in District) ÷ (Total Dairy Credit across India / Total Food & Beverage Sector Credit across India).  
RCA > 1 implies above-average specialization; RCA > 4 is considered strong comparative advantage.")
