import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Load the disaster dataset into a DataFrame
data = pd.read_csv('grouped_df.csv')
df = pd.DataFrame(data)
df['yyyy-mm'] = pd.to_datetime(df['yyyy-mm'], format='%Y-%m')

# Define colors for specific columns
column_colors = {
    "Hurricane": "blue",  # Set 'Hurricanes' to blue
    "Flood": "pink",
    "Severe Storm": "red",
    "Coastal Storm": "yellow",
    "Typhoon": "orange",
    "Earthquake": "Maroon",
    "Snowstorm": "green",
    "Severe Ice Storm": "purple",
    "Fire": "Aqua"
    # Add other column-color mappings as needed
}

for i in range(2010, 2020):  
    # Filter data to include only years 2010 to 2019
    # Step 2: Filter dates between 2010-01 and 2019-12
    start_date = str(i) + '-01'
    end_date = str(i) +'-12'
    filtered_df = df[df['yyyy-mm'].between(start_date, end_date)]
    # Pivot the data to prepare for plotting
    pivot_df = filtered_df.pivot(index="yyyy-mm", columns="incident_name", values="count").fillna(0)


    # Create a figure and axis for the plot
    fig, ax1 = plt.subplots(figsize=(12, 8))
    # Get a list of colors for all columns in the order they appear in the DataFrame
    color_list = [column_colors.get(col, "grey") for col in pivot_df.columns]  # Default color is grey

    # Plot the stacked bar chart
    pivot_df.plot(kind="bar", stacked=True, ax=ax1, color=color_list, cmap="tab20", edgecolor="black")
    ax1.set_title(f"Disaster Counts by Year ({start_date}-{end_date}) with Stock Prices Overlay", fontsize=16)
    ax1.set_xlabel("Year", fontsize=12)
    ax1.set_ylabel("Disaster Count", fontsize=12)
    ax1.legend(title="Incident Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    start_date = str(i) + '-01-01'
    end_date = str(i) +'-12-31'
    # Fetch stock data for AGRO from 2010 to 2019 with daily frequency
    stock_data = yf.download('AGRO', start=start_date, end=end_date, interval='1d')

    # Resample the data by week and calculate the average Close price for each week
    stock_data['Date'] = stock_data.index
    stock_data['Year'] = stock_data['Date'].dt.year

    # Filter to only include data from 2010 to 2019
    stock_data = stock_data[(stock_data['Year'] >= 2010) & (stock_data['Year'] <= 2019)]

    # Resample by week, taking the mean of the closing prices
    weekly_close = stock_data['Close']
    weekly_close.index = weekly_close.index.tz_localize(None)
    weekly_close_aligned = weekly_close.reindex(pivot_df.index, method='nearest')
    # Resample to monthly frequency and take the mean
    monthly_mean = weekly_close.resample('M').mean()

    # Format the index to 'yyyy-mm'
    monthly_mean.index = monthly_mean.index.strftime('%Y-%m')

    # Add the secondary plot (line chart) on the second y-axis
    ax2 = ax1.twinx()
    ax2.plot(monthly_mean.index, monthly_mean.values, color="black", label="AGRO Stock Monthly Close Price", linewidth=2)
    ax2.set_ylabel("Stock Price (USD)", fontsize=12)
    ax2.legend(loc='upper right')

    # Synchronize x-axis labels and set tick parameters
    ax1.set_xticks(range(len(pivot_df.index)))
    ax1.set_xticklabels(pivot_df.index.strftime('%Y-%m'), rotation=45)

    # Final adjustments
    plt.tight_layout()
    plt.show()
