import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Smart Inventory Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# CUSTOM CSS
# -------------------------------
st.markdown("""
<style>

/* Main App */
.stApp {
    background-color: #0f172a;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: linear-gradient(
        145deg,
        #1e293b,
        #111827
    );

    border: 1px solid rgba(255,255,255,0.05);

    padding: 20px;
    border-radius: 18px;

    box-shadow:
        0 4px 15px rgba(0,0,0,0.35);
}

/* Metric Labels */
[data-testid="metric-container"] label {
    color: #94a3b8 !important;
}

/* Charts */
.plot-container {
    border-radius: 15px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# DATABASE
# -------------------------------
conn = sqlite3.connect(
    "data/bakery.db",
    check_same_thread=False
)

# -------------------------------
# DASHBOARD FUNCTION
# -------------------------------
def show_dashboard_page():

    st.title("📊 Smart Inventory Analytics")

    # -------------------------------
    # LOAD DATA
    # -------------------------------
    sales_df = pd.read_sql_query(
        "SELECT * FROM sales",
        conn
    )

    if sales_df.empty:
        st.warning("No sales data available")
        return

    # -------------------------------
    # CLEAN DATA
    # -------------------------------
    sales_df["sale_date"] = pd.to_datetime(
        sales_df["sale_date"],
        errors="coerce"
    )

    sales_df["revenue"] = pd.to_numeric(
        sales_df["revenue"],
        errors="coerce"
    ).fillna(0)

    sales_df["profit"] = pd.to_numeric(
        sales_df["profit"],
        errors="coerce"
    ).fillna(0)

    sales_df = sales_df.dropna(subset=["sale_date"])

    # -------------------------------
    # KPI VALUES
    # -------------------------------
    total_orders = len(sales_df)

    total_revenue = sales_df["revenue"].sum()

    total_profit = sales_df["profit"].sum()

    # -------------------------------
    # KPI SECTION
    # -------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 Total Revenue",
            f"₹{total_revenue:,.0f}"
        )

    with col2:
        st.metric(
            "📈 Total Profit",
            f"₹{total_profit:,.0f}"
        )

    with col3:
        st.metric(
            "🧾 Total Orders",
            total_orders
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------
    # DAILY REVENUE
    # -------------------------------
    daily_revenue = (
        sales_df.groupby(
            sales_df["sale_date"].dt.date
        )["revenue"]
        .sum()
        .reset_index()
    )

    daily_revenue.columns = [
        "date",
        "revenue"
    ]

    st.subheader("📉 Revenue Trend")

    fig1 = px.area(
        daily_revenue,
        x="date",
        y="revenue",
        template="plotly_dark"
    )

    fig1.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white",
        height=450
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # -------------------------------
    # DAILY PROFIT
    # -------------------------------
    daily_profit = (
        sales_df.groupby(
            sales_df["sale_date"].dt.date
        )["profit"]
        .sum()
        .reset_index()
    )

    daily_profit.columns = [
        "date",
        "profit"
    ]

    st.subheader("📊 Profit Trend")

    fig2 = px.line(
        daily_profit,
        x="date",
        y="profit",
        markers=True,
        template="plotly_dark"
    )

    fig2.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white",
        height=450
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -------------------------------
    # TOP PRODUCTS
    # -------------------------------
    st.subheader("🏆 Top Products")

    top_products = (
        sales_df["product_name"]
        .value_counts()
        .reset_index()
    )

    top_products.columns = [
        "product",
        "orders"
    ]

    fig3 = px.bar(
        top_products,
        x="product",
        y="orders",
        color="orders",
        template="plotly_dark"
    )

    fig3.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white",
        height=450
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # -------------------------------
    # RECENT SALES
    # -------------------------------
    st.subheader("🧾 Recent Sales")

    st.dataframe(
        sales_df.sort_values(
            by="sale_date",
            ascending=False
        ).head(10),
        use_container_width=True
    )