import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("Sales Dashboard")

def process_sales_register(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Week'] = df['Date'].dt.strftime('%Y-%U')
    weekly_demand = df.groupby(['Week', 'Product'])['Qty Sold'].sum().reset_index()
    return weekly_demand

if "year_inputs" not in st.session_state:
    st.session_state["year_inputs"] = []

if "available_years" not in st.session_state:
    st.session_state["available_years"] = list(range(2000, 2025))

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
    results_displayed = False
    for entry in st.session_state["year_inputs"]:
        year = entry["year"]
        file = entry["file"]

        if year and file:
            aggregated_df = process_sales_register(file)
            var_name = f"demand_{str(year)[-2:]}"
            st.session_state[var_name] = aggregated_df

            st.subheader(f"Weekly Aggregated Data for {year}")
            st.dataframe(aggregated_df)
            results_displayed = True
        elif not file:
            st.warning(f"Please upload a file for Year {year}")
    if not results_displayed:
        st.write("No valid inputs provided. Please ensure you upload files for the selected years.")
