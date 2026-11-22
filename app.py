import streamlit as st
import pandas as pd
import requests

N8N_API_URL = "http://localhost:5678/webhook/50403f1d-9299-4469-ba7a-f4de2bc1d4dc"

st.set_page_config(
    page_title="ResQChain AI",
    page_icon="🌐",
    layout="wide"
)

# --------------------------------------------------
# Fetch live supply records from the n8n Dashboard API
# --------------------------------------------------
try:
    response = requests.get(N8N_API_URL, timeout=30)
    response.raise_for_status()
    records = response.json()

    # Support lists, single records, and common API wrappers
    if isinstance(records, dict):
        if isinstance(records.get("data"), list):
            records = records["data"]
        elif isinstance(records.get("records"), list):
            records = records["records"]
        else:
            records = [records]

    if not isinstance(records, list) or not records:
        st.error("The API returned no supply records.")
        st.stop()

    data = pd.DataFrame(records)

except (requests.RequestException, ValueError) as e:
    st.error(f"Could not load supply records from n8n: {e}")
    st.stop()

# --------------------------------------------------
# Map Google Sheets columns to dashboard columns
# --------------------------------------------------
data = data.rename(columns={
    "city": "City",
    "supply_name": "Supplier",
    "category": "Product",
    "available_stock_days": "Stock",
    "supplier_lead_time_days": "Delay",
    "disruption_risk": "Risk",
})

# Check essential columns
required_columns = ["City", "Supplier", "Product", "Risk", "Stock", "Delay"]
missing_columns = [col for col in required_columns if col not in data.columns]

if missing_columns:
    st.error(
        "Missing expected columns in the API response: "
        + ", ".join(missing_columns)
    )
    st.stop()

# Clean and convert values
data["City"] = data["City"].fillna("Unknown").astype(str)
data["Supplier"] = data["Supplier"].fillna("Unknown").astype(str)
data["Product"] = data["Product"].fillna("Unknown").astype(str)
data["Risk"] = data["Risk"].fillna("UNKNOWN").astype(str).str.upper().str.strip()

for column in ["Stock", "Delay", "disruption_score"]:
    if column in data.columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.title("🌐 ResQChain AI")
st.sidebar.caption("Intelligent Supply Chain Risk Monitoring")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Risk Analytics", "Supply Records"]
)

cities = sorted(data["City"].unique().tolist())

city_filter = st.sidebar.multiselect(
    "Filter by City",
    cities,
    default=cities
)

filtered = data[data["City"].isin(city_filter)].copy()

# --------------------------------------------------
# Header
# --------------------------------------------------
st.title("🌐 ResQChain AI Dashboard")
st.caption("AI-Powered Supply Chain Risk Monitoring System")
st.caption(f"Records received from n8n: {len(data)}")
st.divider()

# --------------------------------------------------
# Dashboard
# --------------------------------------------------
if page == "Dashboard":
    total = len(filtered)
    high = int((filtered["Risk"] == "HIGH").sum())
    low = int((filtered["Risk"] == "LOW").sum())
    avg_delay = filtered["Delay"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Supply Records", total)
    c2.metric("High Risk", high, delta="Attention Required",
              delta_color="inverse")
    c3.metric("Low Risk", low)
    c4.metric(
        "Avg Lead Time",
        f"{avg_delay:.1f} days" if pd.notna(avg_delay) else "N/A"
    )

    st.subheader("Supply Chain Risk Overview")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Risk Distribution")
        risk_counts = filtered["Risk"].value_counts()
        if not risk_counts.empty:
            st.bar_chart(risk_counts)
        else:
            st.info("No records available for the selected cities.")

    with right:
        st.markdown("#### Average Lead Time by City")
        city_risk = filtered.groupby("City")["Delay"].mean().dropna()
        if not city_risk.empty:
            st.bar_chart(city_risk)
        else:
            st.info("No lead-time data available.")

    st.subheader("🚨 High-Risk Supply Records")
    high_data = filtered[filtered["Risk"] == "HIGH"]

    if not high_data.empty:
        st.dataframe(high_data, use_container_width=True, hide_index=True)
    else:
        st.success("No high-risk records in the selected cities.")

# --------------------------------------------------
# Risk Analytics
# --------------------------------------------------
elif page == "Risk Analytics":
    st.subheader("📊 Risk Analytics")

    st.markdown("#### Risk Category")
    risk_counts = filtered["Risk"].value_counts()

    if not risk_counts.empty:
        st.bar_chart(risk_counts)
    else:
        st.info("No risk data available.")

    st.markdown("#### Supplier Lead Time")
    supplier_delay = filtered.set_index("Supplier")["Delay"].dropna()

    if not supplier_delay.empty:
        st.bar_chart(supplier_delay)
    else:
        st.info("No lead-time data available.")

    st.markdown("#### Available Stock (Days)")
    stock_data = filtered.set_index("City")["Stock"].dropna()

    if not stock_data.empty:
        st.bar_chart(stock_data)
    else:
        st.info("No stock data available.")

    if "disruption_score" in filtered.columns:
        st.markdown("#### Disruption Score by City")
        score_data = (
            filtered.groupby("City")["disruption_score"].mean().dropna()
        )
        if not score_data.empty:
            st.bar_chart(score_data)

# --------------------------------------------------
# Supply Records
# --------------------------------------------------
elif page == "Supply Records":
    st.subheader("📦 Supply Records")

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.download_button(
        "Download CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="resqchain_supply_records.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption("ResQChain AI | AI-Powered Supply Chain Resilience")