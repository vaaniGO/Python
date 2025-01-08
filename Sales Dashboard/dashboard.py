import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Sales Dashboard")

# Helper function to process uploaded CSV files and aggregate weekly data
def process_sales_register(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.strftime('%Y-%U')
    weekly_demand = df.groupby(['Week', 'Product'])['Qty Sold'].sum().reset_index()
    weekly_demand.rename(columns={'Qty Sold': 'Qty Sold'}, inplace=True)
    return weekly_demand

# Sidebar for inputs
with st.sidebar:
    st.header("Input Section")

    # Initialize session state for year inputs and file storage
    if "year_inputs" not in st.session_state:
        st.session_state["year_inputs"] = [{"year": None, "file": None}]

    # Function to add a new input field for year and file
    def add_year_input():
        st.session_state.year_inputs.append({"year": None, "file": None})

    # Display inputs dynamically
    for i, entry in enumerate(st.session_state.year_inputs):
        st.write(f"### Input {i + 1}")

        # Year dropdown
        year = st.selectbox(
            f"Select Year for Input {i + 1}",
            options=list(range(2000, 2025)),
            key=f"year_{i}",
            index=list(range(2000, 2025)).index(entry["year"]) if entry["year"] else 0
        )
        st.session_state.year_inputs[i]["year"] = year

        # File uploader
        file = st.file_uploader(
            f"Upload Sales Register for {year} (CSV format)",
            type="csv",
            key=f"file_{i}"
        )

        # Preserve file in session state
        if file is not None:
            st.session_state.year_inputs[i]["file"] = file

        # Display the current file if already uploaded
        if st.session_state.year_inputs[i]["file"]:
            st.write(f"File uploaded for {year}: {st.session_state.year_inputs[i]['file'].name}")

    # Add button for adding more inputs
    st.button("Add Another Year", on_click=add_year_input)

st.header("Processed Results")

# Process Files button functionality
if st.button("Process Files", key="process_files"):
    all_data = []  # Collect all processed dataframes
    results_displayed = False

    for i, entry in enumerate(st.session_state.year_inputs):
        year = entry["year"]
        file = entry["file"]

        if year and file:
            # Process the file and aggregate the data
            aggregated_df = pd.read_csv(file)

            # Save the processed data into session state
            var_name = f"demand_{str(year)[-2:]}"  # E.g., 'demand_24' for 2024
            st.session_state[var_name] = aggregated_df

            # Display aggregated data
            st.subheader(f"Weekly Aggregated Data for {year}")
            st.dataframe(aggregated_df)
            all_data.append(aggregated_df)
            results_displayed = True

        elif not file:
            st.warning(f"Please upload a file for Year {year}")

    if not results_displayed:
        st.write("No valid inputs provided. Please ensure you upload files for the selected years.")
    else:
        # Combine all processed data for further analysis
        all_data = pd.concat(all_data, ignore_index=True)

        # Ensure the 'Date' column exists for filtering purposes
        if 'Date' not in all_data.columns:
            st.error("The 'Date' column is missing in the aggregated data.")
        else:
            # Ensure 'Date' column is in datetime format
            all_data['Date'] = pd.to_datetime(all_data['Date'])

            # Filter data based on date range
            min_date = all_data['Date'].min().date()  # Get minimum date
            max_date = all_data['Date'].max().date()  # Get maximum date
            date_range = st.date_input(
                "Select date range for analysis",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

            if len(date_range) == 2:
                start_date, end_date = date_range
                # Use .dt.date to compare with date objects
                filtered_data = all_data[
                    (all_data['Date'].dt.date >= start_date) & (all_data['Date'].dt.date <= end_date)
                ]

                # Summary statistics
                total_sales = filtered_data['Qty Sold'].sum()
                avg_daily_sales = (
                    filtered_data.groupby('Date')['Qty Sold'].sum().mean()
                )
                top_product = (
                    filtered_data.groupby('Product')['Qty Sold'].sum().idxmax()
                )

                # Metrics display
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Sales", f"{total_sales:,}")
                col2.metric("Avg Daily Sales", f"{avg_daily_sales:.2f}")
                col3.metric("Top Selling Product", top_product)

                # Weekly sales trend
                weekly_sales = (
                    filtered_data.groupby('Week')['Qty Sold'].sum().reset_index()
                )
                fig_trend = px.line(
                    weekly_sales,
                    x='Week',
                    y='Qty Sold',
                    title='Weekly Sales Trend',
                )
                st.plotly_chart(fig_trend, use_container_width=True)

                # Product-wise sales
                product_sales = (
                    filtered_data.groupby('Product')['Qty Sold']
                    .sum()
                    .sort_values(ascending=False)
                    .reset_index()
                )
                fig_product = px.bar(
                    product_sales,
                    x='Product',
                    y='Qty Sold',
                    title='Product-wise Sales',
                )
                st.plotly_chart(fig_product, use_container_width=True)

                # Heatmap of weekly product sales
                pivot_data = filtered_data.pivot_table(
                    values='Qty Sold', index='Week', columns='Product', aggfunc='sum'
                )
                fig_heatmap = px.imshow(
                    pivot_data, title='Weekly Product Sales Heatmap'
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

                # Insights
                st.subheader("Insights")
                st.write(f"1. The total sales volume for the selected period is {total_sales:,} units.")
                st.write(f"2. On average, {avg_daily_sales:.2f} units are sold daily.")
                st.write(f"3. The top-selling product is '{top_product}'.")
                st.write(f"4. There are {len(product_sales)} different products sold during this period.")

                if len(weekly_sales) > 1:
                    sales_trend = (
                        "increasing"
                        if weekly_sales['Qty Sold'].iloc[-1] > weekly_sales['Qty Sold'].iloc[0]
                        else "decreasing"
                    )
                    st.write(f"5. The overall sales trend appears to be {sales_trend} over the selected period.")

                # Seasonality check
                if len(weekly_sales) >= 52:
                    st.write("6. Potential seasonality in sales:")
                    yearly_pattern = filtered_data.groupby(
                        filtered_data['Date'].dt.month
                    )['Qty Sold'].mean()
                    peak_month = yearly_pattern.idxmax()
                    trough_month = yearly_pattern.idxmin()
                    st.write(f"   - Peak sales typically occur in month {peak_month}")
                    st.write(f"   - Lowest sales typically occur in month {trough_month}")
