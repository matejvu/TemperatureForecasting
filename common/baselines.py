"""Persistence and climatology baseline forecasters.

These are the simplest possible forecasts and serve as sanity-check lower
bars that both the NWP physics baseline and the LSTM should beat.
"""

import numpy as np


def persistence_forecast(last_value: np.ndarray, num_steps: int) -> np.ndarray:
    """Forecast by holding the last observed value constant.

    Args:
        last_value: array of shape (num_features,), the most recent
            observation before the forecast window starts.
        num_steps: number of future steps to forecast.

    Returns:
        Array of shape (num_steps, num_features), the last value repeated
        for every lead time.
    """
    raise NotImplementedError


def climatology_forecast(
    historical_series: np.ndarray,
    num_steps: int,
) -> np.ndarray:
    """Forecast using the historical mean (climatology).

    Args:
        historical_series: array of shape (T, num_features) of past
            observations used to compute the climatological mean. For
            seasonal data (e.g. real weather), this should ideally account
            for time-of-year rather than a single global mean.
        num_steps: number of future steps to forecast.

    Returns:
        Array of shape (num_steps, num_features), the historical mean
        repeated for every lead time.
    """
    raise NotImplementedError
