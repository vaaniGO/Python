import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from prophet import Prophet

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Sales Dashboard")

def process_sales_register(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.strftime('%Y-%U')
    weekly_demand = df.groupby(['Week', 'Product'])['Qty Sold'].sum().reset_index()
    return df, weekly_demand

if "year_inputs" not in st.session_state:
    st.session_state["year_inputs"] = []

if "available_years" not in st.session_state:
    st.session_state["available_years"] = list(range(2001, 2025))

def add_year_input():
    st.session_state["year_inputs"].append({"year": None, "file": None})

def remove_year_input(index):
    if 0 <= index < len(st.session_state["year_inputs"]):
        st.session_state["year_inputs"].pop(index)

with st.sidebar:
    st.header("Upload your sales registers")
    if st.button("Add Another Year"):
        add_year_input()

    for i, entry in enumerate(st.session_state["year_inputs"]):
        col1, col2 = st.columns([8, 2])
        with col1:
            year_key = f"year_{i}"
            file_key = f"file_{i}"

            st.session_state["year_inputs"][i]["year"] = st.selectbox(
                f"Select year for input {i+1}",
                options=[None] + st.session_state["available_years"],
                index=0 if entry["year"] is None else st.session_state["available_years"].index(entry["year"]),
                key=year_key,
            )

            st.session_state["year_inputs"][i]["file"] = st.file_uploader(
                f"Upload Sales Register for {entry['year']}",
                type="csv",
                key=file_key,
            )

        with col2:
            if st.button("❌", key=f"remove_{i}"):
                remove_year_input(i)
                st.rerun()


st.header("Processed Results")

if st.button("Process Files", key="process_files"):
    st.session_state["results_displayed"] = False
    st.session_state["all_data"] = pd.DataFrame()

    for entry in st.session_state["year_inputs"]:
        year = entry["year"]
        file = entry["file"]

        if year and file:
            df, aggregated_df = process_sales_register(file)
            st.session_state["all_data"] = pd.concat([st.session_state["all_data"], df])
            var_name = f"demand_{str(year)[-2:]}"
            st.session_state[var_name] = aggregated_df

            st.subheader(f"Weekly Aggregated Data for {year}")
            st.dataframe(aggregated_df.style.highlight_max(axis=0, color='lightgreen'), use_container_width=True)
            st.session_state["results_displayed"] = True
        elif not file:
            st.warning(f"Please upload a file for Year {year}")

if st.session_state.get("results_displayed", False):
    all_data = st.session_state["all_data"]
    # Date range selection
    min_date = all_data['Date'].min().date()
    max_date = all_data['Date'].max().date()
    date_range = st.date_input("Select date range for analysis", 
                               value=(min_date, max_date),
                               min_value=min_date, 
                               max_value=max_date)

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = all_data[(all_data['Date'].dt.date >= start_date) & (all_data['Date'].dt.date <= end_date)]
        st.session_state["filtered_data"] = filtered_data

        # Summary statistics
        total_sales = filtered_data['Qty Sold'].sum()
        avg_daily_sales = filtered_data.groupby('Date')['Qty Sold'].sum().mean()
        top_product = filtered_data.groupby('Product')['Qty Sold'].sum().idxmax()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", f"{total_sales:,}")
        col2.metric("Avg Daily Sales", f"{avg_daily_sales:.2f}")
        col3.metric("Top Selling Product", top_product)

        # Weekly sales trend
        weekly_sales = filtered_data.groupby('Week')['Qty Sold'].sum().reset_index()
        fig_trend = px.line(weekly_sales, x='Week', y='Qty Sold', title='Weekly Sales Trend')
        st.plotly_chart(fig_trend, use_container_width=True)

        # Product-wise sales
        product_sales = filtered_data.groupby('Product')['Qty Sold'].sum().sort_values(ascending=False).reset_index()
        fig_product = px.bar(product_sales, x='Product', y='Qty Sold', title='Product-wise Sales')
        st.plotly_chart(fig_product, use_container_width=True)

        # Heatmap of weekly product sales
        pivot_data = filtered_data.pivot_table(values='Qty Sold', index='Week', columns='Product', aggfunc='sum')
        fig_heatmap = px.imshow(pivot_data, title='Weekly Product Sales Heatmap')
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Insights
        st.subheader("Insights")
        st.write(f"1. The total sales volume for the selected period is {total_sales:,} units.")
        st.write(f"2. On average, {avg_daily_sales:.2f} units are sold daily.")
        st.write(f"3. The top-selling product is '{top_product}'.")
        st.write(f"4. There are {len(product_sales)} different products sold during this period.")

        # Store product sales for future usage
        st.session_state["product_sales"] = product_sales

# Product-wise demand prediction
if "filtered_data" in st.session_state and "product_sales" in st.session_state:
    st.subheader("Product-wise Demand Prediction")

    product_to_forecast = st.selectbox("Select a product for prediction:", 
                                       st.session_state["product_sales"]['Product'])

    if product_to_forecast:
        filtered_data = st.session_state["filtered_data"]
        product_data = filtered_data[filtered_data['Product'] == product_to_forecast]
        product_data = product_data.groupby('Date')['Qty Sold'].sum().reset_index()
        product_data.columns = ['ds', 'y']

        # Fit Prophet model
        model = Prophet()
        model.fit(product_data)

        # Make future dataframe
        future = model.make_future_dataframe(periods=365)
        forecast = model.predict(future)

        # Aggregate to monthly predictions
        forecast['Month'] = forecast['ds'].dt.to_period('M')
        monthly_forecast = forecast.groupby('Month')['yhat'].sum().reset_index()
        monthly_forecast.columns = ['Month', 'Predicted Demand']

        # Display forecasted table
        st.write(f"Monthly Predicted Demand for {product_to_forecast}:")
        st.dataframe(monthly_forecast)


