import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales EDA Dashboard", layout="wide")
st.title("📊 Sales Data EDA Dashboard")

# Sidebar – Upload
st.sidebar.header("1. Upload Sales CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type=["csv"])

# Encoding fallback loader
def load_csv_with_fallback(file):
    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']
    for enc in encodings:
        try:
            return pd.read_csv(file, encoding=enc)
        except:
            continue
    raise UnicodeDecodeError("Could not decode the CSV file with common encodings.")

if uploaded_file:
    try:
        df = load_csv_with_fallback(uploaded_file)
        st.success("✅ File uploaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to read CSV file: {e}")
        st.stop()

    # Normalize column names to uppercase
    df.columns = df.columns.str.upper()

    # Drop rows that are completely empty
    df.dropna(how='all', inplace=True)

    # Try to convert ORDERDATE to datetime
    if 'ORDERDATE' in df.columns:
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')

    # Handle missing values: fill numeric with 0, categorical with "Unknown"
    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    df[num_cols] = df[num_cols].fillna(0)
    df[cat_cols] = df[cat_cols].fillna("Unknown")

    # Show missing data summary
    with st.expander("🩹 Missing Values Summary"):
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            st.dataframe(missing.to_frame(name="Missing Values"))
        else:
            st.write("✅ No missing values detected (after handling).")

    # ===== Sales Trend Over Time =====
    st.subheader("📈 Sales Trend Over Time")
    if 'ORDERDATE' in df.columns and 'SALES' in df.columns:
        time_df = df[['ORDERDATE', 'SALES']].dropna().sort_values('ORDERDATE')
        fig_time = px.line(time_df, x='ORDERDATE', y='SALES', title="Sales Over Time")
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("ORDERDATE or SALES column missing for time trend plot.")

    # ===== Sales by Product Line =====
    st.subheader("📊 Sales by Product Line")
    if 'PRODUCTLINE' in df.columns and 'SALES' in df.columns:
        cat_df = df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
        fig_bar = px.bar(cat_df, x='PRODUCTLINE', y='SALES', title="Total Sales by Product Line")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("PRODUCTLINE or SALES column missing for bar chart.")

    # ===== Price vs Quantity Ordered =====
    st.subheader("🧭 Price vs Quantity")
    if 'PRICEEACH' in df.columns and 'QUANTITYORDERED' in df.columns:
        fig_scatter = px.scatter(
            df,
            x='QUANTITYORDERED',
            y='PRICEEACH',
            size='SALES' if 'SALES' in df.columns else None,
            color='PRODUCTLINE' if 'PRODUCTLINE' in df.columns else None,
            title="Price vs Quantity Ordered"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("PRICEEACH or QUANTITYORDERED column missing for scatter plot.")

    # ===== Summary Statistics =====
    with st.expander("📋 Summary Statistics"):
        if num_cols:
            st.write("**📐 Numeric Summary**")
            st.dataframe(df[num_cols].describe().T)
        else:
            st.info("No numeric columns available.")
        if cat_cols:
            st.write("**🏷️ Categorical Summary**")
            st.dataframe(df[cat_cols].describe(include='object').T)
        else:
            st.info("No categorical columns available.")

    # ===== Raw Data View =====
    with st.expander("🧾 Raw Data Table"):
        st.dataframe(df)

else:
    st.info("👈 Upload the `sales_data_sample.csv` file to begin exploring.")
