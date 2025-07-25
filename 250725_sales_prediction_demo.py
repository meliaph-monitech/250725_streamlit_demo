import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# App title
st.title("📊 CSV-Based Sales Forecast App with ML Models")

# Upload CSV file
uploaded_file = st.file_uploader("📁 Upload your CSV file with 'year' and 'sales' columns", type=['csv'])

if uploaded_file is not None:
    # Load CSV
    df = pd.read_csv(uploaded_file)

    # Drop the index column if it's present (e.g. "Unnamed: 0")
    if df.columns[0].lower().startswith('unnamed'):
        df = df.drop(columns=[df.columns[0]])

    # Validate columns
    required_columns = {'year', 'sales'}
    if not required_columns.issubset(df.columns):
        st.error(f"CSV must contain the following columns: {required_columns}")
    else:
        # Sort by year
        df = df[['year', 'sales']].dropna()
        df = df.sort_values("year").reset_index(drop=True)

        # Display raw data
        st.write("### ✅ Input Data")
        st.dataframe(df)

        # Plot actual input data
        fig_input = go.Figure()
        fig_input.add_trace(go.Scatter(
            x=df['year'], y=df['sales'],
            mode='lines+markers', name='Actual Sales'
        ))
        fig_input.update_layout(
            title="📈 Input Sales Data",
            xaxis_title="Year",
            yaxis_title="Sales ($)"
        )
        st.plotly_chart(fig_input, use_container_width=True)

        # Prepare data
        X = df[['year']]
        y = df['sales']

        # Predict next 3 years
        last_year = df['year'].max()
        future_years = pd.DataFrame({'year': np.arange(last_year + 1, last_year + 4)})

        st.subheader("🔮 3-Year Sales Forecast from Multiple Models")

        # Define and configure models with better parameters
        models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree Regressor": DecisionTreeRegressor(max_depth=5, min_samples_split=4, random_state=42),
            "Random Forest Regressor": RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42),
            "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=150, learning_rate=0.1, max_depth=4, random_state=42),
            "Support Vector Regressor (SVR)": make_pipeline(StandardScaler(), SVR(C=100, epsilon=0.1, kernel='rbf'))
        }

        # Loop through models and display predictions
        for name, model in models.items():
            # Train
            model.fit(X, y)

            # Predictions
            pred_existing = model.predict(X)
            pred_future = model.predict(future_years)

            # Combine actual + prediction
            plot_years = pd.concat([X, future_years])
            plot_sales = np.concatenate([pred_existing, pred_future])
            labels = ['Historical'] * len(X) + ['Prediction'] * len(future_years)

            # Plotly chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=plot_years['year'][:len(X)],
                y=plot_sales[:len(X)],
                mode='lines+markers',
                name='Historical'
            ))
            fig.add_trace(go.Scatter(
                x=plot_years['year'][len(X):],
                y=plot_sales[len(X):],
                mode='lines+markers',
                name='Prediction',
                line=dict(dash='dash')
            ))
            fig.update_layout(
                title=f"{name} - Sales Forecast",
                xaxis_title="Year",
                yaxis_title="Sales ($)"
            )
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please upload a CSV file to begin.")
