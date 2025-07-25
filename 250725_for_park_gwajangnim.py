import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA Dashboard", layout="wide")
st.title("📊 Interactive CSV Data EDA Dashboard")

# Sidebar – File Upload
st.sidebar.header("1. Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type=["csv"])

# Sidebar – Encoding Option
st.sidebar.header("2. File Encoding")
encoding = st.sidebar.selectbox("Choose file encoding", ["utf-8", "latin1", "ISO-8859-1", "cp1252"], index=0)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding=encoding)
        st.success("✅ File uploaded and data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error reading CSV file: {e}")
        st.stop()

    st.sidebar.header("3. Column Filters")

    # Detect column types
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64", "datetime"]).columns.tolist()

    # Try converting object columns to datetime
    for col in df.columns:
        if col not in date_cols:
            try:
                df[col] = pd.to_datetime(df[col])
                date_cols.append(col)
            except:
                pass

    # ========= Line Plot =========
    st.subheader("📈 Trend Line Plot")
    if date_cols and num_cols:
        line_date_col = st.selectbox("Date Column", date_cols)
        line_y_col = st.selectbox("Numeric Column", num_cols)
        line_df = df[[line_date_col, line_y_col]].dropna().sort_values(line_date_col)
        fig_line = px.line(line_df, x=line_date_col, y=line_y_col, title=f"{line_y_col} over {line_date_col}")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("ℹ️ No date and numeric columns found for line plot.")

    # ========= Bar Plot =========
    st.subheader("📊 Categorical Histogram")
    if cat_cols and num_cols:
        cat_col = st.selectbox("Categorical Column", cat_cols)
        val_col = st.selectbox("Value Column", num_cols)
        agg_df = df.groupby(cat_col)[val_col].mean().reset_index()
        fig_bar = px.bar(agg_df, x=cat_col, y=val_col, title=f"{val_col} by {cat_col}")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("ℹ️ Need categorical and numeric columns for bar chart.")

    # ========= Scatter Plot =========
    st.subheader("🧭 Scatter Plot")
    if len(num_cols) >= 2:
        x_axis = st.selectbox("X Axis", num_cols, index=0)
        y_axis = st.selectbox("Y Axis", num_cols, index=1)
        fig_scatter = px.scatter(df, x=x_axis, y=y_axis, color=cat_cols[0] if cat_cols else None)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("⚠️ Need at least two numeric columns for scatter plot.")

    # ========= Summary Statistics =========
    with st.expander("📋 Summary Statistics"):
        st.write("**Numeric Summary**")
        st.dataframe(df[num_cols].describe())

        if cat_cols:
            st.write("**Categorical Summary**")
            st.dataframe(df[cat_cols].describe().T)

    # ========= Raw Data =========
    with st.expander("🧾 Raw Data Table"):
        st.dataframe(df)

else:
    st.info("👈 Please upload a CSV file to get started.")
