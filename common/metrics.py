"""Evaluation metrics: RMSE (and MAE) as a function of lead time, computed
against the ERA5 ground-truth series.
"""

import numpy as np


def rmse(y_true: np.ndarray, y_pred: np.ndarray, axis=None) -> np.ndarray:
    """Root-mean-squared error between predicted and true values.

    Args:
        y_true: array of true values.
        y_pred: array of predicted values, same shape as y_true.
        axis: axis (or axes) to reduce over. If None, reduces over all
            elements to a single scalar.

    Returns:
        RMSE value(s) as a numpy array or scalar.
    """
    raise NotImplementedError


def mae(y_true: np.ndarray, y_pred: np.ndarray, axis=None) -> np.ndarray:
    """Mean absolute error between predicted and true values.

    Args:
        y_true: array of true values.
        y_pred: array of predicted values, same shape as y_true.
        axis: axis (or axes) to reduce over. If None, reduces over all
            elements to a single scalar.

    Returns:
        MAE value(s) as a numpy array or scalar.
    """
    raise NotImplementedError


def rmse_vs_lead_time(
    y_true: np.ndarray,
    forecasts: dict,
) -> dict:
    """Compute RMSE as a function of lead time for multiple forecast methods.

    This is the core comparison metric: for each method (LSTM, NWP,
    persistence, climatology, ...), compute RMSE at each forecast lead
    time so the methods can be plotted on the same axes.

    Args:
        y_true: array of shape (num_windows, num_lead_times,
            num_features), the true/ground-truth values at each lead time.
        forecasts: dict mapping method name -> array of the same shape as
            y_true, containing that method's forecasts.

    Returns:
        Dict mapping method name -> array of shape (num_lead_times,)
        with the RMSE at each lead time, averaged over windows and
        features.
    """
    raise NotImplementedError
