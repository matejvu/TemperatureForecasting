"""Fetch real single-station historical weather data from the Open-Meteo API.

Two datasets are fetched and joined:

- "Features": Historical Forecast API — a specific NWP model re-run over
  past dates, giving a rich variable set (humidity, wind, cloud cover,
  soil temperature/moisture, ...). This is what the feature-exploration
  notebook and the LSTM train on.
- "NWP baseline": Previous Runs API — archived operational forecast
  output at fixed lead times, the real "official prediction" the LSTM is
  compared against.
"""

import time
from datetime import date, timedelta

import numpy as np
import openmeteo_requests
import pandas as pd
import requests_cache
from openmeteo_requests.Client import OpenMeteoRequestsError
from retry_requests import retry

HISTORICAL_FORECAST_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"
PREVIOUS_RUNS_URL = "https://previous-runs-api.open-meteo.com/v1/forecast"

# Station: Petnica, Serbia.
STATION_NAME = "petnica"
STATION_LAT = 44.2469
STATION_LON = 19.9305

# NWP model providing the historical forecast series.
MODEL = "ncep_gfs_seamless"

# Feature variables to fetch from the Historical Forecast API.
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "rain",
    "showers",
    "snowfall",
    "snow_depth",
    "weather_code",
    "pressure_msl",
    "surface_pressure",
    "cloud_cover",
    "cloud_cover_mid",
    "cloud_cover_low",
    "cloud_cover_high",
    "visibility",
    "wind_speed_10m",
    "wind_speed_80m",
    "wind_direction_10m",
    "wind_direction_80m",
    "wind_gusts_10m",
    "temperature_80m",
    "surface_temperature",
    "soil_temperature_0_to_10cm",
    "soil_temperature_10_to_40cm",
    "soil_moisture_0_to_10cm",
    "soil_moisture_10_to_40cm",
    "soil_moisture_40_to_100cm",
    "soil_temperature_100_to_200cm",
    "soil_temperature_40_to_100cm",
]

# Variables to fetch an NWP baseline forecast for. Kept to the project's
# actual forecasting target rather than all HOURLY_VARIABLES, since not
# every variable makes sense as a forecast-vs-truth comparison.
BASELINE_VARIABLES = ["temperature_2m"]

# Fixed lead times (in days) to evaluate the archived NWP forecasts at.
LEAD_TIME_DAYS = [1, 3, 5, 7]

# Historical Forecast API data is available from 2022 onward.
START_DATE = "2022-01-01"

# Previous Runs (NWP baseline) data is only continuous from Jan 2024
# onward, so it won't cover the full feature history above — rows before
# this date will have missing baseline columns after the join.
BASELINE_START_DATE = "2024-01-01"

# Cached, auto-retrying Open-Meteo client, per the official client example.
_cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
_retry_session = retry(_cache_session, retries=5, backoff_factor=0.2)
_openmeteo = openmeteo_requests.Client(session=_retry_session)


def _weather_api_with_retry(url: str, params: dict, retries: int = 3, wait_seconds: int = 60):
    """Call openmeteo.weather_api, retrying if Open-Meteo's rate limit is hit.

    Open-Meteo returns its per-minute rate limit as an error field on an
    otherwise normal response, not as a retryable HTTP status, so the
    retry_requests session wrapped around the client's connection never
    sees it. This adds a manual retry loop for that specific case.

    Args:
        url: the Open-Meteo API endpoint to call.
        params: request parameters dict.
        retries: number of extra attempts after the first failure.
        wait_seconds: seconds to wait before each retry.

    Returns:
        The list of responses from openmeteo.weather_api().
    """
    for attempt in range(retries + 1):
        try:
            return _openmeteo.weather_api(url, params=params)
        except OpenMeteoRequestsError as e:
            is_rate_limit = "limit exceeded" in str(e).lower()
            if attempt == retries or not is_rate_limit:
                raise
            print(f"Open-Meteo rate limit hit, waiting {wait_seconds}s before retrying...")
            time.sleep(wait_seconds)


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


def fetch_historical_forecast(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    variables: list = HOURLY_VARIABLES,
    model: str = MODEL,
) -> pd.DataFrame:
    """Fetch historical NWP model output from the Open-Meteo Historical Forecast API.

    Args:
        latitude: station latitude.
        longitude: station longitude.
        start_date: ISO date string (YYYY-MM-DD), inclusive start.
        end_date: ISO date string (YYYY-MM-DD), inclusive end.
        variables: list of hourly variable names to request.
        model: Open-Meteo weather model identifier.

    Returns:
        DataFrame indexed by timestamp with one column per variable.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables,
        "models": model,
        "start_date": start_date,
        "end_date": end_date,
    }
    responses = _weather_api_with_retry(HISTORICAL_FORECAST_URL, params)
    return _hourly_response_to_dataframe(responses[0], variables)


def fetch_previous_runs(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    lead_time_days: list = LEAD_TIME_DAYS,
    variables: list = BASELINE_VARIABLES,
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
        variables: list of hourly variable names to request a baseline
            forecast for.

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
    responses = _weather_api_with_retry(PREVIOUS_RUNS_URL, params)
    return _hourly_response_to_dataframe(responses[0], hourly_params)


def align_features_and_baseline(
    features: pd.DataFrame,
    previous_runs: pd.DataFrame,
) -> pd.DataFrame:
    """Left-join the feature series and the NWP baseline forecasts on timestamp.

    Uses a left join (keeping every feature row) rather than an inner
    join, since the NWP baseline only starts in 2024 while the feature
    history goes back to 2022 — the baseline columns are simply NaN for
    timestamps before BASELINE_START_DATE. Drop those rows before
    computing baseline-comparison metrics.

    Args:
        features: DataFrame from fetch_historical_forecast.
        previous_runs: DataFrame from fetch_previous_runs.

    Returns:
        A single DataFrame indexed by timestamp combining feature and
        baseline-forecast columns.
    """
    return features.join(previous_runs, how="left")


def save_dataset_npz(
    df: pd.DataFrame,
    path: str,
    feature_columns: list = HOURLY_VARIABLES,
    baseline_columns: list = None,
):
    """Save the fetched dataset as a compressed .npz for training.

    Stores plain numpy arrays rather than a DataFrame so
    real_data/train_lstm.py can load the dataset directly with np.load,
    without redoing the API fetch or depending on pandas at train time.

    Args:
        df: DataFrame from align_features_and_baseline, indexed by
            timestamp.
        path: output file path (should end in .npz).
        feature_columns: column names holding the Historical Forecast
            API values, in the order they should appear in the saved
            "features" array.
        baseline_columns: column names holding the NWP baseline forecast
            values (e.g. from previous_runs.columns), in the order they
            should appear in the saved "baseline" array. If None, no
            baseline arrays are saved.
    """
    arrays = {
        "timestamps": (df.index.astype("int64") // 10**9),
        "features": df[feature_columns].to_numpy(dtype=np.float32),
        "feature_columns": np.array(feature_columns),
    }
    if baseline_columns:
        arrays["baseline"] = df[baseline_columns].to_numpy(dtype=np.float32)
        arrays["baseline_columns"] = np.array(baseline_columns)
    np.savez_compressed(path, **arrays)


if __name__ == "__main__":
    # The Historical Forecast API has much lower latency than the plain
    # ERA5 archive, but still leave a small safety margin.
    end_date = (date.today() - timedelta(days=2)).isoformat()

    features = fetch_historical_forecast(STATION_LAT, STATION_LON, START_DATE, end_date)

    # Give Open-Meteo's per-minute rate limit a moment to reset before the
    # second large request (the first one above already used several).
    time.sleep(5)

    previous_runs = fetch_previous_runs(
        STATION_LAT, STATION_LON, BASELINE_START_DATE, end_date
    )
    combined = align_features_and_baseline(features, previous_runs)

    csv_path = f"real_data/{STATION_NAME}_data.csv"
    combined.to_csv(csv_path)
    print(f"Saved {len(combined)} rows to {csv_path}")

    npz_path = f"real_data/{STATION_NAME}_data.npz"
    save_dataset_npz(
        combined,
        npz_path,
        feature_columns=list(features.columns),
        baseline_columns=list(previous_runs.columns),
    )
    print(f"Saved {len(combined)} rows to {npz_path}")
