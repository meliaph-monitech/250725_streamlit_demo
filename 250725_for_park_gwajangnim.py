import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA Dashboard", layout="wide")
st.title("📊 Interactive CSV Data EDA Dashboard")

# Sidebar – Upload file
st.sidebar.header("1. Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Upload your CSV", type=["csv"])

def load_csv_with_fallback(file):
    """Try multiple encodings to read CSV."""
    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']
    for enc in encodings:
        try:
            return pd.read_csv(file, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("All encoding attempts failed.")

if uploaded_file:
    try:
        df = load_csv_with_fallback(uploaded_file)
        st.success("✅ File uploaded and data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error reading CSV file: {e}")
        st.stop()

    st.sidebar.header("2. Column Filters")

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
                continue

    # ===== Line Plot =====
    st.subheader("📈 Trend Line Plot")
    if date_cols and num_cols:
        line_date_col = st.selectbox("Date Column", date_cols)
        line_y_col = st.selectbox("Y Axis (Numeric)", num_cols)
        line_df = df[[line_date_col, line_y_col]].dropna().sort_values(line_date_col)
        fig_line = px.line(line_df, x=line_date_col, y=line_y_col,
                           title=f"{line_y_col} over {line_date_col}")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("ℹ️ Line plot skipped: need date and numeric columns.")

    # ===== Categorical Bar Chart =====
    st.subheader("📊 Categorical Histogram")
    if cat_cols and num_cols:
        cat_col = st.selectbox("Categorical Column", cat_cols)
        val_col = st.selectbox("Value (Numeric)", num_cols)
        agg_df = df.groupby(cat_col)[val_col].mean().reset_index()
        fig_bar = px.bar(agg_df, x=cat_col, y=val_col,
                         title=f"{val_col} by {cat_col}")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("ℹ️ Bar chart skipped: need categorical and numeric columns.")

    # ===== Scatter Plot =====
    st.subheader("🧭 Scatter Plot")
    if len(num_cols) >= 2:
        x_axis = st.selectbox("X Axis (Numeric)", num_cols, index=0)
        y_axis = st.selectbox("Y Axis (Numeric)", num_cols, index=1)
        fig_scatter = px.scatter(df, x=x_axis, y=y_axis,
                                 color=cat_cols[0] if cat_cols else None,
                                 title=f"{y_axis} vs {x_axis}")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("ℹ️ Scatter plot skipped: need at least two numeric columns.")

    # ===== Summary Statistics =====
    with st.expander("📋 Summary Statistics"):
        if num_cols:
            st.write("**Numeric Summary**")
            st.dataframe(df[num_cols].describe())
        else:
            st.info("No numeric columns to summarize.")

        if cat_cols:
            st.write("**Categorical Summary**")
            st.dataframe(df[cat_cols].describe(include='object').T)
        else:
            st.info("No categorical columns to summarize.")

    # ===== Raw Data Table =====
    with st.expander("🧾 Raw Data Table"):
        st.dataframe(df)

else:
    st.info("👈 Upload a CSV file to begin exploring your data.")
