# LSTM vs. Physics-Based Forecasting on a Real Weather Station

Comparing a data-driven LSTM forecaster against operational NWP (numerical
weather prediction) forecasts on a single real weather station.

## Project structure

```
real_data/      Open-Meteo data fetching, LSTM training/eval, plotting
common/         Shared LSTM model, metrics (RMSE/MAE), persistence/climatology baselines
requirements.txt
```

## Data source

[Open-Meteo](https://open-meteo.com/) (free, no API key required, JSON output):

- **Ground truth**: Historical Weather API (`/v1/archive`), ERA5 reanalysis
  (though ERA5 is itself a model reanalysis, not a direct measurement,
  which is worth noting in the writeup).
- **Physics baseline**: Previous Runs API — archived operational NWP
  forecast output at fixed lead times (1, 3, 5, 7 days), continuous from
  Jan 2024. This is the actual "official prediction" to compare against,
  sidestepping the need to implement 4D-Var/full NWP.
- **Station**: pick one coordinate pair with good data density (e.g. a
  Central European or North American city).

## Pipeline

1. `real_data/fetch_data.py` — fetch ERA5 ("truth") and Previous Runs
   ("physics baseline") series from Open-Meteo for the chosen station.
2. `real_data/train_lstm.py` — train an LSTM on the ERA5 series.
3. `real_data/evaluate.py` — compute RMSE vs. lead time for the LSTM, the
   archived NWP forecasts, persistence (last value), and climatology
   (historical mean).
4. `real_data/plotting.py` — station-series plots and RMSE-vs-lead-time
   curves.

Run order (once implemented):

```bash
python real_data/fetch_data.py
python real_data/train_lstm.py
python real_data/evaluate.py
python real_data/plotting.py
```

## Important framing

This is an **asymmetric comparison**: operational NWP has access to global
observation networks, satellites, and enormous compute, while the LSTM only
sees single-station historical data. Results should be framed as "how much
can a lightweight data-driven model close the gap to an expensive physics
pipeline," not as a fairness contest — the same framing used by real
ML-weather papers (GraphCast, Pangu-Weather) when comparing against
ERA5/NWP baselines.

## Shared code (`common/`)

- `common/lstm_model.py` — the LSTM architecture.
- `common/metrics.py` — RMSE / MAE computation, RMSE-vs-lead-time helper.
- `common/baselines.py` — persistence (last value) and climatology
  (historical mean) baselines.

## Setup

```bash
pip install -r requirements.txt
```
