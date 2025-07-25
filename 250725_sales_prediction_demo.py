import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR

# Title
st.title("📈 Yearly Sales Prediction App")

# Session state to store input data
if 'data' not in st.session_state:
    st.session_state.data = []

# Input form
with st.form("input_form", clear_on_submit=True):
    year = st.number_input("Enter Year", min_value=1900, max_value=2100, step=1)
    sales = st.number_input("Enter Sales ($)", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Data")
    if submitted:
        st.session_state.data.append({"year": year, "sales": sales})

# Show current input
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data).sort_values("year")
    st.write("### Current Input Data")
    st.dataframe(df)

    # Plot the raw data
    fig_raw = go.Figure()
    fig_raw.add_trace(go.Scatter(x=df['year'], y=df['sales'], mode='lines+markers', name='Actual Sales'))
    fig_raw.update_layout(title="Sales Over Years", xaxis_title="Year", yaxis_title="Sales ($)")
    st.plotly_chart(fig_raw, use_container_width=True)

    if st.button("✅ Finish Input Data & Run Prediction"):
        # Prepare features
        X = df[['year']]
        y = df['sales']

        # Generate future years (next 3 years)
        last_year = df['year'].max()
        future_years = pd.DataFrame({'year': np.arange(last_year + 1, last_year + 4)})

        # Machine learning models
        models = {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(),
            "Random Forest": RandomForestRegressor(),
            "Gradient Boosting": GradientBoostingRegressor(),
            "Support Vector Regressor": SVR()
        }

        for name, model in models.items():
            model.fit(X, y)
            pred_existing = model.predict(X)
            pred_future = model.predict(future_years)

            # Combine data for plotting
            plot_years = pd.concat([X, future_years])
            plot_sales = np.concatenate([pred_existing, pred_future])
            labels = ['Historical'] * len(X) + ['Prediction'] * len(future_years)

            plot_df = pd.DataFrame({
                'Year': plot_years['year'],
                'Sales': plot_sales,
                'Type': labels
            })

            # Plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=plot_df[plot_df['Type']=='Historical']['Year'],
                                     y=plot_df[plot_df['Type']=='Historical']['Sales'],
                                     mode='lines+markers',
                                     name='Historical'))
            fig.add_trace(go.Scatter(x=plot_df[plot_df['Type']=='Prediction']['Year'],
                                     y=plot_df[plot_df['Type']=='Prediction']['Sales'],
                                     mode='lines+markers',
                                     name='Prediction',
                                     line=dict(dash='dash')))
            fig.update_layout(title=f"{name} - Sales Forecast",
                              xaxis_title="Year", yaxis_title="Sales ($)")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please start inputting data (Year and Sales).")
