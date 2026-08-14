import pandas as pd
from sklearn.metrics import mean_squared_error
import os
import numpy as np
import matplotlib.pyplot as plt

#ucitavanje i sredjivanje podataka

df=pd.read_csv("/home/polaznik/Desktop/nevena/TemperatureForecasting/real_data/berlin_data.csv")
print(df.head())

df = df.iloc[600:]

df = df.reset_index(drop=True)
total_missing_rows = df.isna().any(axis=1).sum()
print("hello nema ovoliko", total_missing_rows)



#srednja kvadratna greska

y_true = df['temperature_2m']
y_pred = df['temperature_2m_previous_day1']


mse = mean_squared_error(y_true, y_pred)

print("srednja kvadratna greska", mse)

"""



#RELATIVNA GRESKA

###relativna greska za svaki podatak (recorded temp vs predvidjena)

def relativna(temperature_2m, temperature_2m_previous_day1):
 
    y_true = df[temperature_2m]
    y_pred = df[temperature_2m_previous_day1]

    y_true_masked = y_true.replace(0, np.nan)

    relative_errors = np.abs(
        (y_true_masked - y_pred)/ y_true_masked )

    return relative_errors


df["date"] = pd.to_datetime(df["date"])


greska1d= relativna("temperature_2m", "temperature_2m_previous_day1")
greska3d= relativna("temperature_2m", "temperature_2m_previous_day3")
greska5d= relativna("temperature_2m", "temperature_2m_previous_day5")
greska7d= relativna("temperature_2m", "temperature_2m_previous_day7")

#linijski grafik relativnih greski

plt.figure(figsize=(12, 6))

plt.plot(df["date"], greska1d, label="1 dan")
plt.plot(df["date"], greska3d, label="3 dana")
plt.plot(df["date"], greska5d, label="5 dana", color="blue")

plt.xlabel("vreme")
plt.ylabel("relativna greska")
plt.title("Relativna greška predikcija temperature")
plt.legend()
plt.grid(True)


plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



###Srednja relativna

relativna1d= relativna("temperature_2m","temperature_2m_previous_day1")
relativna3d= relativna("temperature_2m","temperature_2m_previous_day3")
relativna5d= relativna("temperature_2m","temperature_2m_previous_day5")
relativna7d= relativna("temperature_2m","temperature_2m_previous_day7")

print("dan1 relativna",relativna1d)

greske = [relativna1d.mean(), relativna3d.mean(), relativna5d.mean(), relativna7d.mean()]
nazivi = ["1 dan", "3 dana", "5 dana", "7 dana"]

plt.figure(figsize=(8, 5))

plt.bar(nazivi, greske, color=["blue", "orange", "green", "yellow"])

plt.xlabel("broj dana")
plt.ylabel("relativna greska")
plt.title("srednja relativna greska")

plt.grid(axis="y", alpha=0.3)
plt.show()

"""
#KVADRATNA

#vreme vs greska

df["date"] = pd.to_datetime(df["date"])

def kvadratna(danas, predvidjanje):
    
    y_true = df[danas]
    y_pred = df[predvidjanje]

    squared_errors = (y_true - y_pred) ** 2

    return squared_errors

kgreska1d= kvadratna("temperature_2m", "temperature_2m_previous_day1")
kgreska3d= kvadratna("temperature_2m", "temperature_2m_previous_day3")
kgreska5d= kvadratna("temperature_2m", "temperature_2m_previous_day5")
kgreska7d= kvadratna("temperature_2m", "temperature_2m_previous_day7")


plt.figure(figsize=(12, 6))

plt.plot(df["date"], kgreska1d, label="1 dan")
plt.plot(df["date"], kgreska3d, label="3 dana")
plt.plot(df["date"], kgreska5d, label="5 dana")
plt.plot(df["date"], kgreska7d, label="7 dana", color="blue")

plt.xlabel("vreme")
plt.ylabel("kvadratna greska")
plt.title("kvadratna greška predikcija temperature")
plt.legend()
plt.grid(True)


plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#srednje kvadratne grseske

"""
def srednjakvadratna(temperature_2m, temperature_2m_previous_day1):
   
    y_true = df[temperature_2m]
    y_pred = df[temperature_2m_previous_day1]
    mse = mean_squared_error(y_true, y_pred)

    return mse


srkgreska1d= srednjakvadratna("temperature_2m", "temperature_2m_previous_day1")
srkgreska3d= srednjakvadratna("temperature_2m", "temperature_2m_previous_day3")
srkgreska5d= srednjakvadratna("temperature_2m", "temperature_2m_previous_day5")
srkgreska7d= srednjakvadratna("temperature_2m", "temperature_2m_previous_day7")

print("dan1 srednja kvadratna",srkgreska1d)

greske = [srkgreska1d, srkgreska3d, srkgreska5d, srkgreska7d]
nazivi = ["1 dan", "3 dana", "5 dana", "7 dana"]

plt.figure(figsize=(8, 5))

plt.bar(nazivi, greske, color=["blue", "orange", "green", "yellow"])

plt.xlabel("broj dana")
plt.ylabel("srednja kvadratna greska")
plt.title("srednja kvadratna greska")

plt.grid(axis="y", alpha=0.3)
plt.show()
"""


temp = df['temperature_2m']
prognoza1d = df['temperature_2m_previous_day1']
prognoza7d = df['temperature_2m_previous_day7']


def plot(y1,y2,y3):
    plt.figure(figsize=(12, 6))

    plt.plot(df["date"], y1, label=" dan")
    plt.plot(df["date"], y2, label="1 dana")
    plt.plot(df["date"], y3, label="7 dana")


    plt.xlabel("vreme")
    plt.ylabel("temperatura")
    plt.title("stvarna temperaura i predikcije")
    plt.legend()
    plt.grid(True)


    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

plot(temp,prognoza1d,prognoza7d)