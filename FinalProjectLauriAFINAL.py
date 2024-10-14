import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

electricity_data = pd.read_csv('https://raw.githubusercontent.com/lauriansa/School/refs/heads/main/Electricity_20-09-2024.csv', sep=';', decimal=',')
price_data = pd.read_csv('https://raw.githubusercontent.com/lauriansa/School/refs/heads/main/sahkon-hinta-010121-240924.csv', sep=',')

# Convert time columns to datetime
electricity_data['Time'] = pd.to_datetime(electricity_data['Time'], format=' %d.%m.%Y %H:%M')
price_data['Time'] = pd.to_datetime(price_data['Time'], format='%d-%m-%Y %H:%M:%S')

# Merge datasets on Time
merged_data = pd.merge(electricity_data, price_data, on='Time', how='inner')

# Calculate the total bill based on energy consumption and price
merged_data['Bill'] = (merged_data['Energy (kWh)'] * merged_data['Price (cent/kWh)']) / 100

# Group data by time period and calculate desired values
def calculate_grouped_values(merged_data, time_period):
    grouped_data = merged_data.groupby(pd.Grouper(key='Time', freq=time_period)).agg(
        {'Energy (kWh)': 'sum', 'Bill': 'sum', 'Price (cent/kWh)': 'mean', 'Temperature': 'mean'}
    ).reset_index()
    grouped_data.rename(columns={'Energy (kWh)': 'Total Energy (kWh)', 'Bill': 'Total Bill', 
                                 'Price (cent/kWh)': 'Average Price (cent/kWh)', 
                                 'Temperature': 'Average Temperature'}, inplace=True)
    return grouped_data

# Streamlit part
st.title("Final project")

# Time selector
start_date = st.date_input("Select start date", merged_data['Time'].min().date())
end_date = st.date_input("Select end date", merged_data['Time'].max().date())

# Filter data 
filtered_data = merged_data[(merged_data['Time'] >= pd.Timestamp(start_date)) & (merged_data['Time'] <= pd.Timestamp(end_date))]

# Grouping selector (hourly, daily, weekly)
grouping_interval = st.selectbox("Select grouping interval", options=['H', 'D', 'W'], format_func=lambda x: {'H': 'Hourly', 'D': 'Daily', 'W': 'Weekly'}[x])

# Calculate grouped data based on selected interval
grouped_data = calculate_grouped_values(filtered_data, grouping_interval)

# Show statistics over the selected period
st.subheader(f"Statistics from {start_date} to {end_date}")
st.write(f"**Total Consumption:** {grouped_data['Total Energy (kWh)'].sum():,.2f} kWh")
st.write(f"**Total Bill:** {grouped_data['Total Bill'].sum():,.2f} €")
st.write(f"**Average Price:** {grouped_data['Average Price (cent/kWh)'].mean():,.2f} cents/kWh")
st.write(f"**Average Temperature:** {grouped_data['Average Temperature'].mean():,.2f} °C")

# Own graphs for consumption, price, bill and temp
st.subheader("Visualizations")

fig, axs = plt.subplots(4, 1, figsize=(10, 16))

# Electricity Consumption
axs[0].plot(grouped_data['Time'], grouped_data['Total Energy (kWh)'], color='tab:blue')
axs[0].set_title('Electricity Consumption (kWh)')
axs[0].set_ylabel('kWh')
axs[0].set_xlabel('Time')


# Electricity Price
axs[1].plot(grouped_data['Time'], grouped_data['Average Price (cent/kWh)'], color='tab:blue')
axs[1].set_title('Electricity Price (cents/kWh)')
axs[1].set_ylabel('cents/kWh')
axs[1].set_xlabel('Time')

# Electricity Bill
axs[2].plot(grouped_data['Time'], grouped_data['Total Bill'], color='tab:blue')
axs[2].set_title('Electricity Bill (€)')
axs[2].set_ylabel('€')
axs[2].set_xlabel('Time')

# Temperature
axs[3].plot(grouped_data['Time'], grouped_data['Average Temperature'], color='tab:blue')
axs[3].set_title('Temperature (°C)')
axs[3].set_ylabel('°C')
axs[3].set_xlabel('Time')
#plt.tight_layout()
st.pyplot(fig)
