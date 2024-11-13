import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('loan approval data/train.csv')

class_distribution = df['Loan_Status'].value_counts()
class_percentage = df['Loan_Status'].value_counts(normalize = True)*100

# Convert all binary string variables (Yes/No) to 0/1
df['Married'] = df['Married'].map({'No': 0, 'Yes': 1})
df['Education'] = df['Education'].map({'Graduate':1, 'Not Graduate':0})
df['Property_Area'] = df['Property_Area'].map({'Urban':1, 'Rural':0})
df['Loan_Status'] = df['Loan_Status'].map({'Y':1, 'N':0})
df['Gender'] = df['Gender'].map({'Male': 1, 'Female':0})
df['Self_Employed'] = df['Self_Employed'].map({'Yes': 1, 'No': 0})
df.head()

# Drop the column containg values like 'Loan id' that are not relevant to the heatmap
df = df.drop(columns=['Loan_ID'])
# Replace values that cannot be converted to numeric values to NaN
df = df.apply(pd.to_numeric, errors='coerce')
# Convert all values to float for the purpose of the heatmap
df = df.astype(float)
# Make the correlation heatmap
df_corr = df.corr()

# Plot the correlation heatmap using pyplot
plt.figure(figsize=(10, 8))
sns.heatmap(df_corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Matrix Heatmap")
plt.show()

# The correlation heatmap gives us variables to focus on. We have identified a 0.57 correlation
# between LoanAmount and LoanStatus, and a 0.56 correlation between CreditHistory and LoanAmount
# So our two points of focus are these variables
# However, there are a few more interesting results: There is a slight negative correlation
# between applicant income and coapplicant income, between married and loan term
# and between loan term and property area. We can also study these variables only to see
# how they vary with each other

