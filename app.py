import streamlit as st
import pandas as pd
import requests

# --------------------------------------------------
# Page configuration and connection settings
# --------------------------------------------------
st.set_page_config(
    page_title="ResQChain AI | Supply Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Secure n8n connection through Streamlit Secrets
try:
    N8N_API_URL = st.secrets["N8N_API_URL"]
except (KeyError, FileNotFoundError):
    st.error("N8N_API_URL is missing. Please configure Streamlit Secrets.")
    st.stop()
# --------------------------------------------------
# Professional dark theme (CSS)
# --------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --bg: #07111f;
        --panel: #101d2e;
        --panel-2: #14243a;
        --line: rgba(148, 163, 184, .16);
        --text: #e8f0fb;
        --muted: #91a4bb;
        --cyan: #35c6f4;
        --blue: #4b8df8;
        --green: #36d399;
        --red: #fb7185;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 15% 0%, rgba(36, 99, 160, .18), transparent 34%),
            linear-gradient(145deg, #07111f 0%, #0a1626 55%, #081321 100%);
        color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(7, 17, 31, .72); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b192a 0%, #0a1422 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { color: #dce8f7; }
    .block-container { padding-top: 2rem; padding-bottom: 2.5rem; max-width: 1500px; }
    h1, h2, h3 { color: #f2f7ff !important; letter-spacing: -.025em; }
    p, label, [data-testid="stCaptionContainer"] { color: var(--muted); }
    .hero {
        padding: 1.45rem 1.7rem;
        border: 1px solid rgba(80, 160, 220, .24);
        border-radius: 20px;
        background: linear-gradient(115deg, rgba(19, 48, 77, .96), rgba(16, 29, 46, .88));
        box-shadow: 0 18px 50px rgba(0,0,0,.18);
        margin-bottom: 1.2rem;
    }
    .hero-kicker { color: #6ed7ff; text-transform: uppercase; font-size: .72rem;
        letter-spacing: .16em; font-weight: 800; }
    .hero-title { color: #f5f9ff; font-size: clamp(1.65rem, 3vw, 2.45rem);
        font-weight: 800; margin: .25rem 0; }
    .hero-sub { color: #a9bdd3; font-size: .96rem; }
    .metric-card {
        background: linear-gradient(145deg, rgba(20,36,58,.98), rgba(13,27,44,.98));
        border: 1px solid var(--line); border-radius: 16px;
        padding: 1rem 1.1rem; min-height: 116px;
        box-shadow: 0 10px 28px rgba(0,0,0,.12);
    }
    .metric-label { color: #9eb2c9; font-size: .78rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: .08em; }
    .metric-value { color: #f3f8ff; font-size: 1.9rem; font-weight: 800; margin-top: .35rem; }
    .metric-note { color: #8ca3bc; font-size: .78rem; margin-top: .15rem; }
    .section-label { color: #dcecff; font-size: 1.08rem; font-weight: 750; margin: .7rem 0; }
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        border: 1px solid var(--line); border-radius: 13px; overflow: hidden;
    }
    .status-pill { display: inline-block; padding: .28rem .65rem; border-radius: 99px;
        background: rgba(54,211,153,.12); color: #65e6b4; font-size: .75rem; font-weight: 700; }
    .small-muted { color: #8fa4bc; font-size: .8rem; }
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 10px; border: 1px solid rgba(80,160,220,.35);
        background: linear-gradient(100deg, #176a9d, #2563b9);
        color: white; font-weight: 700;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        border-color: #67d5ff; color: white; filter: brightness(1.12);
    }
    hr { border-color: var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Data retrieval
# --------------------------------------------------
@st.cache_data(ttl=60, show_spinner=False)
def fetch_records(api_url: str):
    response = requests.get(api_url, timeout=20)
    response.raise_for_status()
    payload = response.json()

    if isinstance(payload, dict):
        if isinstance(payload.get("data"), list):
            payload = payload["data"]
        elif isinstance(payload.get("records"), list):
            payload = payload["records"]
        else:
            payload = [payload]

    if not isinstance(payload, list):
        raise ValueError("The webhook response must be a list of records.")
    return pd.DataFrame(payload)


st.sidebar.markdown("## 🌐 ResQChain AI")
st.sidebar.caption("DISASTER RELIEF • SUPPLY INTELLIGENCE")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "WORKSPACE",
    ["Dashboard", "Risk Analytics", "Supply Records"],
    label_visibility="visible",
)

try:
    with st.spinner("Connecting to ResQChain data services..."):
        data = fetch_records(N8N_API_URL)
    connection_ok = True
    connection_message = "Live data connection"
except (requests.RequestException, ValueError) as exc:
    connection_ok = False
    connection_message = str(exc)
    data = pd.DataFrame()

if not connection_ok:
    st.markdown(
        '<div class="hero"><div class="hero-kicker">ResQChain AI • Operations</div>'
        '<div class="hero-title">Supply intelligence workspace</div>'
        '<div class="hero-sub">The dashboard is available, but the n8n data service could not be reached.</div></div>',
        unsafe_allow_html=True,
    )
    st.error("Unable to load live supply records from n8n.")
    st.caption("Check that the n8n container and public tunnel are running, and that N8N_API_URL in Streamlit Secrets is current.")
    with st.expander("Connection details"):
        st.code(connection_message)
    st.stop()

# --------------------------------------------------
# Normalize source fields
# --------------------------------------------------
data = data.rename(columns={
    "city": "City",
    "supply_name": "Supplier",
    "category": "Product",
    "available_stock_days": "Stock",
    "supplier_lead_time_days": "Delay",
    "disruption_risk": "Risk",
})

required_columns = ["City", "Supplier", "Product", "Risk", "Stock", "Delay"]
missing_columns = [column for column in required_columns if column not in data.columns]
if missing_columns:
    st.error("Missing expected fields in the n8n response: " + ", ".join(missing_columns))
    st.stop()

for column in ["City", "Supplier", "Product"]:
    data[column] = data[column].fillna("Unknown").astype(str)
data["Risk"] = data["Risk"].fillna("UNKNOWN").astype(str).str.upper().str.strip()
for column in ["Stock", "Delay", "disruption_score"]:
    if column in data.columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

cities = sorted(data["City"].unique().tolist())
city_filter = st.sidebar.multiselect("FILTER BY CITY", cities, default=cities)
filtered = data[data["City"].isin(city_filter)].copy()

st.sidebar.markdown("---")
st.sidebar.markdown('<span class="status-pill">● CONNECTED</span>', unsafe_allow_html=True)
st.sidebar.caption(f"{len(data):,} records received • refresh interval 60 sec")
if st.sidebar.button("↻ Refresh live data", use_container_width=True):
    fetch_records.clear()
    st.rerun()

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    '<div class="hero">'
    '<div class="hero-kicker">Resilience • Response • Readiness</div>'
    '<div class="hero-title">ResQChain AI</div>'
    '<div class="hero-sub">AI-powered disaster relief supply chain monitoring and risk intelligence</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="small-muted">WORKSPACE / {page.upper()} &nbsp; • &nbsp; '
    f'<span class="status-pill">LIVE DATA CONNECTED</span> &nbsp; • &nbsp; '
    f'{len(data):,} total records</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Dashboard
# --------------------------------------------------
if page == "Dashboard":
    total = len(filtered)
    high = int((filtered["Risk"] == "HIGH").sum())
    medium = int((filtered["Risk"] == "MEDIUM").sum())
    low = int((filtered["Risk"] == "LOW").sum())
    avg_delay = filtered["Delay"].mean()
    avg_stock = filtered["Stock"].mean()

    metrics = [
        ("TOTAL SUPPLY RECORDS", f"{total:,}", "Across selected locations"),
        ("HIGH-RISK RECORDS", f"{high:,}", "Requires priority attention"),
        ("MEDIUM-RISK RECORDS", f"{medium:,}", "Monitor closely"),
        ("AVERAGE LEAD TIME", f"{avg_delay:.1f} days" if pd.notna(avg_delay) else "N/A", "Supplier delivery duration"),
    ]
    cols = st.columns(4)
    for col, (label, value, note) in zip(cols, metrics):
        col.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Supply chain risk overview</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown("**Risk distribution**")
        risk_counts = filtered["Risk"].value_counts()
        if not risk_counts.empty:
            st.bar_chart(risk_counts, color="#35c6f4")
        else:
            st.info("No risk data for the selected locations.")
    with right:
        st.markdown("**Average lead time by city**")
        city_delay = filtered.groupby("City")["Delay"].mean().dropna().sort_values(ascending=False)
        if not city_delay.empty:
            st.bar_chart(city_delay, color="#4b8df8")
        else:
            st.info("No lead-time data available.")

    st.markdown('<div class="section-label">🚨 Priority high-risk supply records</div>', unsafe_allow_html=True)
    high_data = filtered[filtered["Risk"] == "HIGH"]
    if not high_data.empty:
        st.dataframe(high_data, use_container_width=True, hide_index=True)
    else:
        st.success("No high-risk records in the selected locations.")

# --------------------------------------------------
# Risk analytics
# --------------------------------------------------
elif page == "Risk Analytics":
    st.markdown('<div class="section-label">Risk intelligence & operational indicators</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("High risk", int((filtered["Risk"] == "HIGH").sum()))
    b.metric("Average stock cover", f"{filtered['Stock'].mean():.1f} days" if pd.notna(filtered["Stock"].mean()) else "N/A")
    b.metric("Average lead time", f"{filtered['Delay'].mean():.1f} days" if pd.notna(filtered["Delay"].mean()) else "N/A")

    left, right = st.columns(2)
    with left:
        st.markdown("**Risk category breakdown**")
        counts = filtered["Risk"].value_counts()
        if not counts.empty:
            st.bar_chart(counts, color="#35c6f4")
        else:
            st.info("No risk data available.")
    with right:
        st.markdown("**Supplier lead time (days)**")
        supplier_delay = filtered.groupby("Supplier")["Delay"].mean().dropna().sort_values(ascending=False)
        if not supplier_delay.empty:
            st.bar_chart(supplier_delay, color="#4b8df8")
        else:
            st.info("No supplier lead-time data available.")

    st.markdown("**Available stock by city (days)**")
    stock_by_city = filtered.groupby("City")["Stock"].mean().dropna().sort_values(ascending=False)
    if not stock_by_city.empty:
        st.bar_chart(stock_by_city, color="#36d399")
    else:
        st.info("No stock data available.")

    if "disruption_score" in filtered.columns:
        st.markdown("**Average disruption score by city**")
        score_by_city = filtered.groupby("City")["disruption_score"].mean().dropna().sort_values(ascending=False)
        if not score_by_city.empty:
            st.bar_chart(score_by_city, color="#fb7185")

# --------------------------------------------------
# Supply records
# --------------------------------------------------
elif page == "Supply Records":
    st.markdown('<div class="section-label">Supply inventory register</div>', unsafe_allow_html=True)
    search = st.text_input("Search records", placeholder="Search city, supplier, product or risk...")
    view = filtered.copy()
    if search:
        searchable = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False))
        view = view[searchable.any(axis=1)]

    risk_options = ["All"] + sorted(view["Risk"].dropna().unique().tolist())
    selected_risk = st.selectbox("Filter by risk", risk_options)
    if selected_risk != "All":
        view = view[view["Risk"] == selected_risk]

    st.caption(f"Showing {len(view):,} of {len(filtered):,} records")
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇ Download filtered records (CSV)",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="resqchain_supply_records.csv",
        mime="text/csv",
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.markdown(
    '<div class="small-muted">RESQCHAIN AI &nbsp; • &nbsp; AI-POWERED SUPPLY CHAIN RESILIENCE'
    '<br>Operational visibility for faster, better-informed disaster response.</div>',
    unsafe_allow_html=True,
)
