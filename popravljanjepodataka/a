import pandas as pd



df=pd.read_csv("/home/polaznik/Desktop/nevena/TemperatureForecasting/real_data/berlin_data.csv")
print(df.head())
"""
df = df.dropna(how="any")  
print(f"Cleaned dataset shape: {df.shape}")
print(df.head())

df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")

# 3. Force a complete, continuous time grid
# Use 'h' for hourly, 'D' for daily, '15min' for 15-minute intervals, etc.
df = df.asfreq("h")

# 4. Interpolate missing values smoothly
# 'time' interpolation considers the exact time spacing between points
df["temperature_2m_previous_day1"] = df["temperature_2m_previous_day1"].interpolate(method="time")
print(df.head)

"""

df = df.iloc[600:]

df = df.reset_index(drop=True)
print(df.head)

total_missing_rows = df.isna().any(axis=1).sum()
print("hello nema ovoliko", total_missing_rows)

