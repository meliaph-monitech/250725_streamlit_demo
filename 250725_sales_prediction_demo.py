import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales EDA Dashboard", layout="wide")
st.title("📊 Sales Data EDA Dashboard")

st.sidebar.header("1. Upload Sales CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type=["csv"])

# Column index mapping based on provided order
COL_IDX = {
    "ORDERNUMBER": 0,
    "QUANTITYORDERED": 1,
    "PRICEEACH": 2,
    "ORDERLINENUMBER": 3,
    "SALES": 4,
    "ORDERDATE": 5,
    "PRODUCTLINE": 10,
}

def load_csv_with_fallback(file):
    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']
    for enc in encodings:
        try:
            return pd.read_csv(file, encoding=enc)
        except:
            continue
    raise UnicodeDecodeError("Could not decode the CSV file.")

if uploaded_file:
    try:
        df = load_csv_with_fallback(uploaded_file)
        st.success("✅ File uploaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to read CSV file: {e}")
        st.stop()

    # Drop fully empty rows
    df.dropna(how='all', inplace=True)

    # Check if the DataFrame has enough columns
    if df.shape[1] <= max(COL_IDX.values()):
        st.error("❌ The uploaded file does not contain all required columns.")
        st.stop()

    # Convert ORDERDATE (index 5) to datetime
    try:
        orderdate_col = df.columns[COL_IDX["ORDERDATE"]]
        df[orderdate_col] = pd.to_datetime(df[orderdate_col], errors='coerce')
    except Exception as e:
        st.warning(f"⚠️ Failed to convert ORDERDATE: {e}")

    # Fill missing values
    num_cols = df.select_dtypes(include='number').columns
    obj_cols = df.select_dtypes(include='object').columns
    df[num_cols] = df[num_cols].fillna(0)
    df[obj_cols] = df[obj_cols].fillna("Unknown")

    # Missing value report
    with st.expander("🩹 Missing Values Summary"):
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            st.dataframe(missing.to_frame(name="Missing Values"))
        else:
            st.write("✅ No missing values detected (after handling).")

    # ===== Sales Trend Over Time =====
    st.subheader("📈 Sales Trend Over Time")
    try:
        sales_col = df.columns[COL_IDX["SALES"]]
        date_col = df.columns[COL_IDX["ORDERDATE"]]
        time_df = df[[date_col, sales_col]].dropna().sort_values(date_col)
        time_df.columns = ['ORDERDATE', 'SALES']
        fig_time = px.line(time_df, x='ORDERDATE', y='SALES', title="Sales Over Time")
        st.plotly_chart(fig_time, use_container_width=True)
    except Exception as e:
        st.info(f"Could not plot Sales Trend: {e}")

    # ===== Sales by Product Line =====
    st.subheader("📊 Sales by Product Line")
    try:
        prod_col = df.columns[COL_IDX["PRODUCTLINE"]]
        sales_col = df.columns[COL_IDX["SALES"]]
        prod_df = df[[prod_col, sales_col]].copy()
        prod_df.columns = ['PRODUCTLINE', 'SALES']
        grouped = prod_df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
        fig_bar = px.bar(grouped, x='PRODUCTLINE', y='SALES', title="Total Sales by Product Line")
        st.plotly_chart(fig_bar, use_container_width=True)
    except Exception as e:
        st.info(f"Could not plot Product Line Sales: {e}")

    # ===== Price vs Quantity Scatter =====
    st.subheader("🧭 Price vs Quantity")
    try:
        qty_col = df.columns[COL_IDX["QUANTITYORDERED"]]
        price_col = df.columns[COL_IDX["PRICEEACH"]]
        sales_col = df.columns[COL_IDX["SALES"]]
        prod_col = df.columns[COL_IDX["PRODUCTLINE"]]
        scatter_df = df[[qty_col, price_col, sales_col, prod_col]].copy()
        scatter_df.columns = ['QUANTITYORDERED', 'PRICEEACH', 'SALES', 'PRODUCTLINE']
        fig_scatter = px.scatter(
            scatter_df,
            x='QUANTITYORDERED',
            y='PRICEEACH',
            size='SALES',
            color='PRODUCTLINE',
            title="Price vs Quantity Ordered"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    except Exception as e:
        st.info(f"Could not plot Price vs Quantity: {e}")

    # ===== Summary Statistics =====
    with st.expander("📋 Summary Statistics"):
        if not df.select_dtypes(include='number').empty:
            st.write("**📐 Numeric Summary**")
            st.dataframe(df.describe().T)
        if not df.select_dtypes(include='object').empty:
            st.write("**🏷️ Categorical Summary**")
            st.dataframe(df.describe(include='object').T)

    # ===== Raw Data Table =====
    with st.expander("🧾 Raw Data Table"):
        st.dataframe(df)

else:
    st.info("👈 Upload the `sales_data_sample.csv` file to begin exploring.")
