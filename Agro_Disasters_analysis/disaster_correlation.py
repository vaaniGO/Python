import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Step 1: Creating the calamity DataFrame
data = pd.read_csv('grouped_df.csv')
calamity_df = pd.DataFrame(data)
calamity_df = calamity_df.groupby("yyyy-mm")["count"].sum().reset_index()
calamity_df = calamity_df.set_index("yyyy-mm")

# Step 2: Downloading AGRO stock price data
agro = yf.download("AGRO", start="2011-01-01", end="2019-12-31")

# Step 3: Resampling stock prices to monthly mean
agro_monthly = agro["Close"].resample("M").mean()  # Produces a Series
agro_monthly.index = agro_monthly.index.to_period("M").astype(str)  # Convert to 'yyyy-mm' format

# Step 4: Aligning calamity and stock price data
merged_df = calamity_df.join(agro_monthly, how="inner")
merged_df.columns = ["Calamity Count", "AGRO Close Price"]

# Step 5: Calculating correlation
correlation = merged_df.corr()
print("Correlation Matrix:")
print(correlation)

# Step 6: Adding best-fit line
x = merged_df["Calamity Count"]
y = merged_df["AGRO Close Price"]

# Perform linear regression to get the slope and intercept
slope, intercept = np.polyfit(x, y, 1)  # 1 means linear regression

# Generate predicted values for the trend line
best_fit_line = slope * x + intercept

# Plotting the scatter plot and best-fit line
plt.figure(figsize=(10, 5))
plt.scatter(x, y, alpha=0.7, color="blue", label="Data Points")
plt.plot(x, best_fit_line, color="red", linewidth=2, label="Best-Fit Line")

# Adding labels and title
plt.title("Correlation between Calamity Count and AGRO Close Price (Monthly)")
plt.xlabel("Calamity Count")
plt.ylabel("AGRO Close Price")
plt.grid()
plt.legend()
plt.show()
