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

    inventory_df = pd.read_sql_query(
        "SELECT * FROM inventory",
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
    # DATE FILTER
    # -------------------------------

    st.sidebar.header("Filters")

    min_date = sales_df["sale_date"].min().date()
    max_date = sales_df["sale_date"].max().date()

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter dataframe
    sales_df = sales_df[
        (sales_df["sale_date"].dt.date >= start_date) &
        (sales_df["sale_date"].dt.date <= end_date)
    ]

    if sales_df.empty:
        st.warning("No data available for the selected date range.")
        return
    # -------------------------------
    # PRODUCT FILTER
    # -------------------------------

    products = ["All"] + sorted(
        sales_df["product_name"].unique().tolist()
    )

    selected_product = st.sidebar.selectbox(
        "Select Product",
        products
    )

    if selected_product != "All":
        sales_df = sales_df[
            sales_df["product_name"] == selected_product
        ]

    if sales_df.empty:
        st.warning("No data available for the selected product.")
        return

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
    # EXECUTIVE SUMMARY
    # -------------------------------

    st.subheader("📌 Executive Summary")

    highest_revenue_product = (
        sales_df.groupby("product_name")["revenue"]
        .sum()
        .idxmax()
    )

    highest_profit_product = (
        sales_df.groupby("product_name")["profit"]
        .sum()
        .idxmax()
    )

    average_order_value = (
        sales_df["revenue"].mean()
    )

    total_products = inventory_df["item_name"].nunique()

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        st.info(f"""
    **Highest Revenue Product**
    {highest_revenue_product}

    **Highest Profit Product**
    {highest_profit_product}
    """)

    with summary_col2:
        st.info(f"""
    **Average Order Value**
    ₹{average_order_value:.2f}

    **Products in Inventory**
    {total_products}
    """)
    # -------------------------------
    # INVENTORY OVERVIEW
    # -------------------------------

    st.subheader("📦 Inventory Overview")

    col1, col2, col3 = st.columns(3)

    low_stock = inventory_df[
        inventory_df["quantity"] <=
        inventory_df["reorder_threshold"]
    ]

    with col1:
        st.metric(
            "Products in Inventory",
            len(inventory_df)
        )

    with col2:
        st.metric(
            "Total Stock",
            int(inventory_df["quantity"].sum())
        )

    with col3:
        st.metric(
            "Low Stock Items",
            len(low_stock)
        )
        if not low_stock.empty:

            st.warning("⚠️ Low Stock Items")

            st.dataframe(
                low_stock[
                    [
                        "item_name",
                        "quantity",
                        "reorder_threshold"
                    ]
                ],
                use_container_width=True
            )

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
    # MONTHLY REVENUE
    # -------------------------------

    monthly_revenue = (
        sales_df
        .groupby(
            sales_df["sale_date"].dt.to_period("M")
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly_revenue["sale_date"] = (
        monthly_revenue["sale_date"]
        .astype(str)
    )

    st.subheader("📅 Monthly Revenue")

    fig_month = px.bar(
        monthly_revenue,
        x="sale_date",
        y="revenue",
        color="revenue",
        template="plotly_dark"
    )

    fig_month.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white",
        height=450
    )

    st.plotly_chart(
        fig_month,
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
    # MONTHLY PROFIT
    # -------------------------------

    monthly_profit = (
        sales_df
        .groupby(
            sales_df["sale_date"].dt.to_period("M")
        )["profit"]
        .sum()
        .reset_index()
    )

    monthly_profit["sale_date"] = (
        monthly_profit["sale_date"]
        .astype(str)
    )

    st.subheader("📅 Monthly Profit")

    fig_month_profit = px.bar(
        monthly_profit,
        x="sale_date",
        y="profit",
        color="profit",
        template="plotly_dark"
    )

    fig_month_profit.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white",
        height=450
    )

    st.plotly_chart(
        fig_month_profit,
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
    # REVENUE DISTRIBUTION
    # -------------------------------

    st.subheader("🥧 Revenue Distribution by Product")

    product_revenue = (
        sales_df
        .groupby("product_name")["revenue"]
        .sum()
        .reset_index()
    )

    fig4 = px.pie(
        product_revenue,
        names="product_name",
        values="revenue",
        template="plotly_dark",
        hole=0.4
    )

    fig4.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font_color="white",
        height=500
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )
    # -------------------------------
    # DOWNLOAD REPORT
    # -------------------------------

    st.subheader("📥 Download Dashboard Report")

    csv = sales_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Sales Report (CSV)",
        data=csv,
        file_name="sales_report.csv",
        mime="text/csv"
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