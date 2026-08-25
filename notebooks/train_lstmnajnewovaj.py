#!/usr/bin/env python
# coding: utf-8

# In[183]:

import pandas as pd
from sklearn.metrics import mean_squared_error
import os
import numpy as np
import matplotlib.pyplot as plt
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import torch
import torch.optim as optim
import tqdm
import torch
import numpy as np
from torch import nn


# In[184]:





LOOKBACK = 24


# In[ ]:


df=pd.read_csv("/home/polaznik/Desktop/nevena/TemperatureForecasting/real_data/petnica_data.csv")
timeseries = df[["temperature_2m"]].values.astype('float32')


trening = df.loc[df["date"] < "2024-08-14", ["temperature_2m"]].values.astype("float32")

validacija = df.loc[
    (df["date"] >= "2024-08-14") & (df["date"] < "2025-08-14"),
    ["temperature_2m"]
].values.astype("float32")

test= df.loc[
    df["date"] >= "2025-08-14",
    ["temperature_2m"]
].values.astype("float32")

train_size=int(len(trening))
val_size = int(len(validacija))
test_size=int(len(test))

#deli podatke na prozore od len(dataset)-lookback-1 i za svaki i daje x i y feature ili target

import torch

def create_dataset(dataset, lookback):
    """Transform a time series into a prediction dataset

    Args:
        dataset: A numpy array of time series, first dimension is the time steps
        lookback: Size of window for prediction
    """
    X, y = [], []
    for i in range(len(dataset)-lookback):
        feature = dataset[i:i+lookback]
        target = dataset[i+lookback]
        # target = dataset[i+lookback:i+lookback+24]
        X.append(feature)
        y.append(target)
    return torch.tensor(np.array(X)), torch.tensor(np.array(y))


X_train, y_train = create_dataset(trening, lookback=LOOKBACK) # matrice x_train ulazne sekvence duzine lookback, y_train-ciljevi/targeti
X_val, y_val = create_dataset(validacija, lookback=LOOKBACK)


# In[208]:


print(X_train.shape, X_val.shape, y_train.shape, y_val.shape)

"""
# In[ ]:

class AirModel(nn.Module):
    def __init__(self, hidden_size=64, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, 1)
    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x[:, -1, :])
        return x


"""
a=64

class AirModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=a, num_layers=1, batch_first=True)
        self.linear = nn.Linear(a, 1) # TODO: treba li dodati nelinearnost
        # self.linear = nn.Linear(a, 24)
    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x[:, -1, :])
        #x = self.linear(x)
        return x


import numpy as np
import torch.optim as optim
import torch.utils.data as data

model = AirModel()
optimizer = optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.MSELoss()
loader = data.DataLoader(data.TensorDataset(X_train, y_train), shuffle=True, batch_size=8)


# In[217]:


print(model.lstm)


# In[218]:


num_params = np.sum([p.numel() for p in model.parameters()])
print(f"Nasa mreza ima {num_params} parametara")


# In[219]:


input_example = X_train[-1, :, :].unsqueeze(0)
output_example = model(input_example)
print(input_example.shape, output_example.shape)


# In[220]:


"""
# In[221]:
import itertools

hidden_sizes = [16, 32, 64, 128]
num_layers_list = [1, 2, 3]
learning_rates = [0.01, 0.001, 0.0001]

results = []

for hidden_size, num_layers, lr in itertools.product(hidden_sizes, num_layers_list, learning_rates):

    model = AirModel(hidden_size=hidden_size, num_layers=num_layers)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    loader = data.DataLoader(data.TensorDataset(X_train, y_train), shuffle=True, batch_size=8)

    train_losses = []
    val_losses = []
    n_epochs = 5
    for epoch in range(n_epochs):
        model.train()
        epoch_losses = []
        for X_batch, y_batch in loader:
            y_pred = model(X_batch)
            loss = loss_fn(y_pred, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_losses.append(loss.item())
        train_losses.append(sum(epoch_losses)/len(epoch_losses))
        model.eval()
        with torch.no_grad():
            y_pred = model(X_val)
            val_loss = loss_fn(y_pred, y_val)
        val_losses.append(val_loss.item())

    print(f"hidden_size={hidden_size}, num_layers={num_layers}, lr={lr} -> val MSE %.4f" % val_losses[-1])
    results.append({"hidden_size": hidden_size, "num_layers": num_layers, "lr": lr, "val_loss": val_losses[-1]})

results_df = pd.DataFrame(results).sort_values("val_loss")
print(results_df)

"""
train_losses = []
val_losses = []
n_epochs = 5
for epoch in range(n_epochs):
    model.train()
    epoch_losses = []
    for X_batch, y_batch in tqdm.tqdm(loader):
        y_pred = model(X_batch)
        loss = loss_fn(y_pred, y_batch)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_losses.append(loss.item())
    train_losses.append(sum(epoch_losses)/len(epoch_losses))
    # Validation
    model.eval()
    with torch.no_grad():
        y_pred = model(X_val)
        val_loss = loss_fn(y_pred, y_val)
    val_losses.append(val_loss.item())
    print("Epoch %d: train MSE %.4f, test MSE %.4f" % (epoch, train_losses[-1], val_losses[-1]))


# In[222]:


plt.figure()
plt.plot(train_losses, label="Trening loss")
plt.plot(val_losses, label="Valdicaija loss")
plt.legend()
plt.show()


# In[223]:


torch.save(model.state_dict(), f"modeli/lstm_.pt")


# In[225]:


# Predikcije u buducnost
model.eval()
predictions = []
time_steps = 1000
with torch.no_grad():
    current_temps = X_train[-1, :, :]
    for i in tqdm.tqdm(range(time_steps)):
        next_temp = model(current_temps.unsqueeze(0))
        predictions.append(next_temp.item())
        current_temps = torch.roll(current_temps, -1)
        current_temps[-1] = next_temp.item()


# In[230]:


predictions = np.array(predictions)
# predictions = torch.cat(predictions, dim=0).squeeze().numpy()


# In[231]:


plt.figure()
plt.plot(validacija[:time_steps])
plt.plot(predictions)


# In[ ]:




