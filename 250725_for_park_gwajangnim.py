import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales EDA Dashboard", layout="wide")
st.title("📊 Sales Data EDA Dashboard")

st.sidebar.header("1. Upload Sales CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type=["csv"])

# Column index mapping (fixed based on column order you provided)
COL_IDX = {
    "ORDERDATE": 5,
    "SALES": 4,
    "PRODUCTLINE": 10,
    "PRICEEACH": 2,
    "QUANTITYORDERED": 1,
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

    # Handle date parsing
    try:
        df.iloc[:, COL_IDX["ORDERDATE"]] = pd.to_datetime(df.iloc[:, COL_IDX["ORDERDATE"]], errors='coerce')
    except:
        st.warning("⚠️ Failed to parse ORDERDATE column.")

    # Handle missing values: numeric = 0, object = "Unknown"
    num_cols = df.select_dtypes(include='number').columns
    obj_cols = df.select_dtypes(include='object').columns
    df[num_cols] = df[num_cols].fillna(0)
    df[obj_cols] = df[obj_cols].fillna("Unknown")

    # Show missing summary
    with st.expander("🩹 Missing Values Summary"):
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            st.dataframe(missing.to_frame(name="Missing Values"))
        else:
            st.write("✅ No missing values detected (after handling).")

    # ===== Trend Over Time =====
    st.subheader("📈 Sales Trend Over Time")
    try:
        time_df = df.iloc[:, [COL_IDX["ORDERDATE"], COL_IDX["SALES"]]].dropna().sort_values(df.columns[COL_IDX["ORDERDATE"]])
        time_df.columns = ['ORDERDATE', 'SALES']
        fig_time = px.line(time_df, x='ORDERDATE', y='SALES', title="Sales Over Time")
        st.plotly_chart(fig_time, use_container_width=True)
    except Exception as e:
        st.info(f"Could not plot Sales Trend: {e}")

    # ===== Sales by Product Line =====
    st.subheader("📊 Sales by Product Line")
    try:
        product_df = df.iloc[:, [COL_IDX["PRODUCTLINE"], COL_IDX["SALES"]]].copy()
        product_df.columns = ['PRODUCTLINE', 'SALES']
        grouped = product_df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
        fig_bar = px.bar(grouped, x='PRODUCTLINE', y='SALES', title="Total Sales by Product Line")
        st.plotly_chart(fig_bar, use_container_width=True)
    except Exception as e:
        st.info(f"Could not plot Product Line Sales: {e}")

    # ===== Scatter Plot =====
    st.subheader("🧭 Price vs Quantity")
    try:
        scatter_df = df.iloc[:, [COL_IDX["QUANTITYORDERED"], COL_IDX["PRICEEACH"], COL_IDX["SALES"], COL_IDX["PRODUCTLINE"]]].copy()
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

    # ===== Summary Stats =====
    with st.expander("📋 Summary Statistics"):
        if not df.select_dtypes(include='number').empty:
            st.write("**📐 Numeric Summary**")
            st.dataframe(df.describe().T)
        if not df.select_dtypes(include='object').empty:
            st.write("**🏷️ Categorical Summary**")
            st.dataframe(df.describe(include='object').T)

    # ===== Raw Data View =====
    with st.expander("🧾 Raw Data Table"):
        st.dataframe(df)

else:
    st.info("👈 Upload the `sales_data_sample.csv` file to begin exploring.")
