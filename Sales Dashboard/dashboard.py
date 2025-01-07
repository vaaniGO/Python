import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Sales Dashboard")

# Helper function to process uploaded CSV files and aggregate weekly data
def process_sales_register(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.strftime('%Y-%U')
    weekly_demand = df.groupby(['Week', 'Product'])['Qty Sold'].sum().reset_index()
    weekly_demand.rename(columns={'Qty Sold': 'Weekly Qty Sold'}, inplace=True)
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

if st.button("Process Files", key="process_files"):
    results_displayed = False
    for i, entry in enumerate(st.session_state.year_inputs):
        year = entry["year"]
        file = entry["file"]

        if year and file:
            aggregated_df = process_sales_register(file)

            var_name = f"demand_{str(year)[-2:]}"  # E.g., 'demand_24' for 2024
            st.session_state[var_name] = aggregated_df

            st.subheader(f"Weekly Aggregated Data for {year}")
            st.dataframe(aggregated_df)
            results_displayed = True

        elif not file:
            st.warning(f"Please upload a file for Year {year}")

    if not results_displayed:
        st.write("No valid inputs provided. Please ensure you upload files for the selected years.")