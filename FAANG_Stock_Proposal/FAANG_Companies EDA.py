
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Libraries imported successfully!")


# In[75]:


import os

local_path = r'C:\Users\rutu5\Desktop\BigDataProject'

# List all files in the directory
files = os.listdir(local_path)
print(files)


# In[76]:


import pandas as pd

local_path = r'C:\Users\rutu5\Desktop\BigDataProject'

# Load individual files
amazon_df = pd.read_csv(os.path.join(local_path, 'Amazon.csv'))
apple_df = pd.read_csv(os.path.join(local_path, 'Apple.csv'))
facebook_df = pd.read_csv(os.path.join(local_path, 'Facebook.csv'))
google_df = pd.read_csv(os.path.join(local_path, 'Google.csv'))
netflix_df = pd.read_csv(os.path.join(local_path, 'Netflix.csv'))

# Display the first few rows of Amazon data
print(amazon_df.head())


# In[77]:


print(amazon_df.info())
print(amazon_df.describe())


# In[10]:


import seaborn as sns


# In[72]:


# Add a source column to track the dataset origin
amazon_df['Source'] = 'Amazon'
apple_df['Source'] = 'Apple'
facebook_df['Source'] = 'Facebook'
google_df['Source'] = 'Google'
netflix_df['Source'] = 'Netflix'

# Concatenate all datasets
all_data = pd.concat([amazon_df, apple_df, facebook_df, google_df, netflix_df], ignore_index=True)

# Check the combined dataset
print(all_data.head())


# In[28]:


# Average closing prices by company
avg_close = all_data.groupby('Source')['Close'].mean()
print(avg_close)


# In[30]:


import seaborn as sns
print(sns.__version__)


# In[38]:


get_ipython().system('pip install --upgrade seaborn')


# In[40]:


import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
for source in all_data['Source'].unique():
    subset = all_data[all_data['Source'] == source]
    plt.plot(subset['Date'], subset['Close'], label=source)

plt.title('Closing Prices Over Time for FAANG Companies')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend()
plt.show()


# In[70]:


# Add a column to indicate the data source
amazon_df['Source'] = 'Amazon'
apple_df['Source'] = 'Apple'
facebook_df['Source'] = 'Facebook'
google_df['Source'] = 'Google'
netflix_df['Source'] = 'Netflix'

# Combine all datasets
all_data = pd.concat([amazon_df, apple_df, facebook_df, google_df, netflix_df], ignore_index=True)

# Convert 'Date' column to datetime format
all_data['Date'] = pd.to_datetime(all_data['Date'])

# Normalize the 'Close' column
all_data['Normalized_Close'] = all_data.groupby('Source')['Close'].transform(lambda x: x / x.iloc[0])

# Display the combined data
print(all_data.head())


# In[81]:


import pandas as pd
import matplotlib.pyplot as plt

# Assuming amazon_df is your dataframe
# Correctly parse the 'Date' column
try:
    amazon_df["Date"] = pd.to_datetime(amazon_df["Date"], format="%Y-%m-%d")
except ValueError:
    print("Date parsing failed. Check the format of the 'Date' column.")
    print(amazon_df["Date"].head())

# Plot the Closing Prices
plt.figure(figsize=(12, 6))
plt.plot(amazon_df["Date"], amazon_df["Close"], label="Amazon Closing Prices", marker="o", markersize=2)

# Title and labels
plt.title("Amazon Closing Prices Over Time", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Closing Price", fontsize=12)

# Customize ticks
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Add grid and legend
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()

# Show the plot
plt.show()


# In[88]:


import pandas as pd
import matplotlib.pyplot as plt

# Assuming amazon_df is your dataframe
# Correctly parse the 'Date' column
try:
    apple_df["Date"] = pd.to_datetime(apple_df["Date"], format="%Y-%m-%d")
except ValueError:
    print("Date parsing failed. Check the format of the 'Date' column.")
    print(apple_df["Date"].head())

# Plot the Closing Prices
plt.figure(figsize=(12, 6))
plt.plot(apple_df["Date"], apple_df["Close"], label="Apple Closing Prices", marker="o", markersize=2)

# Title and labels
plt.title("Apple Closing Prices Over Time", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Closing Price", fontsize=12)

# Customize ticks
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Add grid and legend
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()

# Show the plot
plt.show()


# In[82]:


import pandas as pd
import matplotlib.pyplot as plt

# Assuming amazon_df is your dataframe
# Correctly parse the 'Date' column
try:
    apple_df["Date"] = pd.to_datetime(apple_df["Date"], format="%Y-%m-%d")
except ValueError:
    print("Date parsing failed. Check the format of the 'Date' column.")
    print(apple_df["Date"].head())

# Plot the Closing Prices
plt.figure(figsize=(12, 6))
plt.plot(apple_df["Date"], apple_df["Close"], label="Apple Closing Prices", marker="o", markersize=2)

# Title and labels
plt.title("Apple Closing Prices Over Time", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Closing Price", fontsize=12)

# Customize ticks
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Add grid and legend
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()

# Show the plot
plt.show()


# In[89]:


import pandas as pd
import matplotlib.pyplot as plt

# Assuming amazon_df is your dataframe
# Correctly parse the 'Date' column
try:
    facebook_df["Date"] = pd.to_datetime(facebook_df["Date"], format="%Y-%m-%d")
except ValueError:
    print("Date parsing failed. Check the format of the 'Date' column.")
    print(facebook_df["Date"].head())

# Plot the Closing Prices
plt.figure(figsize=(12, 6))
plt.plot(facebook_df["Date"], facebook_df["Close"], label="Facebook Closing Prices", marker="o", markersize=2)

# Title and labels
plt.title("Facebook Closing Prices Over Time", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Closing Price", fontsize=12)

# Customize ticks
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Add grid and legend
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()

# Show the plot
plt.show()


# In[90]:


import pandas as pd
import matplotlib.pyplot as plt

# Assuming amazon_df is your dataframe
# Correctly parse the 'Date' column
try:
    netflix_df["Date"] = pd.to_datetime(netflix_df["Date"], format="%Y-%m-%d")
except ValueError:
    print("Date parsing failed. Check the format of the 'Date' column.")
    print(netflix_df["Date"].head())

# Plot the Closing Prices
plt.figure(figsize=(12, 6))
plt.plot(netflix_df["Date"], netflix_df["Close"], label="Netflix Closing Prices", marker="o", markersize=2)

# Title and labels
plt.title("Netflix Closing Prices Over Time", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Closing Price", fontsize=12)

# Customize ticks
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Add grid and legend
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()

# Show the plot
plt.show()


# In[91]:


import pandas as pd
import matplotlib.pyplot as plt

# Assuming amazon_df is your dataframe
# Correctly parse the 'Date' column
try:
    google_df["Date"] = pd.to_datetime(google_df["Date"], format="%Y-%m-%d")
except ValueError:
    print("Date parsing failed. Check the format of the 'Date' column.")
    print(google_df["Date"].head())

# Plot the Closing Prices
plt.figure(figsize=(12, 6))
plt.plot(google_df["Date"], google_df["Close"], label="Google Closing Prices", marker="o", markersize=2)

# Title and labels
plt.title("Google Closing Prices Over Time", fontsize=16)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Closing Price", fontsize=12)

# Customize ticks
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Add grid and legend
plt.grid(True)
plt.legend(fontsize=12)
plt.tight_layout()

# Show the plot
plt.show()


# In[51]:


# Check null values for individual datasets
print("Null values in Amazon dataset:")
print(amazon_df.isnull().sum())
print("\nNull values in Apple dataset:")
print(apple_df.isnull().sum())
print("\nNull values in Facebook dataset:")
print(facebook_df.isnull().sum())
print("\nNull values in Google dataset:")
print(google_df.isnull().sum())
print("\nNull values in Netflix dataset:")
print(netflix_df.isnull().sum())


# In[52]:


# Fill null values with the mean of each column
netflix_df_filled = netflix_df.fillna(netflix_df.mean())

# Verify null values are handled
print("Null values in Netflix dataset after filling with mean:")
print(netflix_df_filled.isnull().sum())


# In[92]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Assuming `all_data` is already combined and available
# Example combining all data:
# all_data = pd.concat([amazon_df, apple_df, facebook_df, google_df, netflix_df], ignore_index=True)

# Generating a correlation heatmap for all numerical columns in the dataset
plt.figure(figsize=(10, 8))
correlation_matrix = all_data.select_dtypes(include=['float64', 'int64']).corr()
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
plt.title("Correlation Heatmap for All Data")
plt.show()

