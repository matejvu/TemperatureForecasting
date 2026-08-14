"""Fetch real single-station weather data from the Open-Meteo API.

Two datasets are needed, both free and requiring no API key:

- "Truth": Historical Weather API (/v1/archive), ERA5 reanalysis — used as
  ground truth (though ERA5 is itself a model reanalysis, not a direct
  measurement, which is worth noting in the writeup).
- "Physics baseline": Previous Runs API — archived operational NWP
  forecast output at fixed lead times, the real "official prediction" to
  compare the LSTM against.
"""

from datetime import date, timedelta

import numpy as np
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
PREVIOUS_RUNS_URL = "https://previous-runs-api.open-meteo.com/v1/forecast"

# Station: pick one coordinate pair with dense observation coverage
# (e.g. a Central European or North American city). Defaults to Berlin.
STATION_NAME = "petnica"
STATION_LAT = 44.2469
STATION_LON = 19.9305

# Variables to fetch (e.g. temperature, pressure, ...).
HOURLY_VARIABLES = ["temperature_2m", "surface_pressure"]

# Fixed lead times (in days) to evaluate the archived NWP forecasts at.
LEAD_TIME_DAYS = [1, 3, 5, 7]

# Previous Runs data is only continuous from Jan 2024 onward.
START_DATE = "2024-01-01"

# Cached, auto-retrying Open-Meteo client, per the official client example.
_cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
_retry_session = retry(_cache_session, retries=5, backoff_factor=0.2)
_openmeteo = openmeteo_requests.Client(session=_retry_session)


def _hourly_response_to_dataframe(response, column_names: list) -> pd.DataFrame:
    """Turn an openmeteo_requests hourly response into a timestamp-indexed DataFrame.

    Args:
        response: a single response object from openmeteo.weather_api(),
            as returned for one location/model.
        column_names: names to assign to the hourly variables, in the
            same order they were requested in the "hourly" param list.

    Returns:
        DataFrame indexed by UTC timestamp with one column per name in
        column_names.
    """
    hourly = response.Hourly()
    data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }
    for i, name in enumerate(column_names):
        data[name] = hourly.Variables(i).ValuesAsNumpy()
    return pd.DataFrame(data=data).set_index("date")


def fetch_era5_truth(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    variables: list = HOURLY_VARIABLES,
) -> pd.DataFrame:
    """Fetch ERA5 reanalysis data from the Open-Meteo Historical Weather API.

    This series is treated as "truth" for both training the LSTM and
    evaluating all methods (LSTM, NWP baseline, persistence, climatology).

    Args:
        latitude: station latitude.
        longitude: station longitude.
        start_date: ISO date string (YYYY-MM-DD), inclusive start.
        end_date: ISO date string (YYYY-MM-DD), inclusive end.
        variables: list of hourly variable names to request.

    Returns:
        DataFrame indexed by timestamp with one column per variable.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": variables,
    }
    responses = _openmeteo.weather_api(ARCHIVE_URL, params=params)
    return _hourly_response_to_dataframe(responses[0], variables)


def fetch_previous_runs(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    lead_time_days: list = LEAD_TIME_DAYS,
    variables: list = HOURLY_VARIABLES,
) -> pd.DataFrame:
    """Fetch archived operational NWP forecasts from the Open-Meteo Previous Runs API.

    Retrieves, for each timestamp, what an operational NWP model actually
    forecast at fixed lead times in the past (e.g. what the 3-day-ahead
    forecast said for this timestamp, issued 3 days earlier). This is the
    physics-based baseline the LSTM is compared against. Each requested
    variable is suffixed "_previous_day{N}" per the Previous Runs API
    convention, giving one column per (variable, lead_time) combination.

    Args:
        latitude: station latitude.
        longitude: station longitude.
        start_date: ISO date string (YYYY-MM-DD), inclusive start.
        end_date: ISO date string (YYYY-MM-DD), inclusive end.
        lead_time_days: list of forecast lead times (in days) to fetch.
        variables: list of hourly variable names to request.

    Returns:
        DataFrame indexed by timestamp with one column per
        (variable, lead_time) combination, named "{variable}_previous_day{N}".
    """
    hourly_params = [
        f"{variable}_previous_day{lead}"
        for variable in variables
        for lead in lead_time_days
    ]
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": hourly_params,
    }
    responses = _openmeteo.weather_api(PREVIOUS_RUNS_URL, params=params)
    return _hourly_response_to_dataframe(responses[0], hourly_params)


def align_truth_and_forecasts(
    truth: pd.DataFrame,
    previous_runs: pd.DataFrame,
) -> pd.DataFrame:
    """Align the ERA5 truth series and the Previous Runs forecasts on a common timestamp index.

    Args:
        truth: DataFrame from fetch_era5_truth.
        previous_runs: DataFrame from fetch_previous_runs.

    Returns:
        A single DataFrame indexed by timestamp combining truth and
        forecast columns, keeping only timestamps present in both.
    """
    return truth.join(previous_runs, how="inner")


def save_dataset_npz(
    df: pd.DataFrame,
    path: str,
    truth_columns: list,
    forecast_columns: list,
):
    """Save the aligned truth+forecast dataset as a compressed .npz for training.

    Stores plain numpy arrays rather than a DataFrame so
    real_data/train_lstm.py can load the dataset directly with
    np.load, without redoing the API fetch or depending on pandas at
    train time.

    Args:
        df: DataFrame from align_truth_and_forecasts, indexed by
            timestamp (as returned by align_truth_and_forecasts).
        path: output file path (should end in .npz).
        truth_columns: column names holding ERA5 truth values, in the
            order they should appear in the saved "truth" array.
        forecast_columns: column names holding archived NWP forecast
            values, in the order they should appear in the saved
            "forecasts" array.
    """
    np.savez_compressed(
        path,
        timestamps=(df.index.astype("int64") // 10**9),
        truth=df[truth_columns].to_numpy(dtype=np.float32),
        truth_columns=np.array(truth_columns),
        forecasts=df[forecast_columns].to_numpy(dtype=np.float32),
        forecast_columns=np.array(forecast_columns),
    )


if __name__ == "__main__":
    # Historical Weather API data lags a few days behind today.
    end_date = (date.today() - timedelta(days=5)).isoformat()

    truth = fetch_era5_truth(STATION_LAT, STATION_LON, START_DATE, end_date)
    previous_runs = fetch_previous_runs(STATION_LAT, STATION_LON, START_DATE, end_date)
    combined = align_truth_and_forecasts(truth, previous_runs)

    csv_path = f"real_data/{STATION_NAME}_data.csv"
    combined.to_csv(csv_path)
    print(f"Saved {len(combined)} rows to {csv_path}")

    npz_path = f"real_data/{STATION_NAME}_data.npz"
    save_dataset_npz(
        combined,
        npz_path,
        truth_columns=list(truth.columns),
        forecast_columns=list(previous_runs.columns),
    )
    print(f"Saved {len(combined)} rows to {npz_path}")
