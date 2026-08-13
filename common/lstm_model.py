"""LSTM forecasting model for single-station weather forecasting."""

import torch
import torch.nn as nn


class ForecastLSTM(nn.Module):
    """Sequence-to-one (or sequence-to-sequence) LSTM forecaster.

    Takes a window of past observations and predicts one or more future
    steps of real ERA5 station data.
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        forecast_horizon: int = 1,
        dropout: float = 0.0,
    ):
        """Build the LSTM forecaster.

        Args:
            input_size: number of input features per timestep (number of
                weather variables).
            hidden_size: number of hidden units per LSTM layer.
            num_layers: number of stacked LSTM layers.
            output_size: number of variables predicted per forecast step.
            forecast_horizon: number of future steps to predict.
            dropout: dropout probability between stacked LSTM layers.
        """
        super().__init__()
        raise NotImplementedError

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Run the forward pass.

        Args:
            x: input tensor of shape (batch, seq_len, input_size).

        Returns:
            Predicted future values of shape
            (batch, forecast_horizon, output_size).
        """
        raise NotImplementedError


def make_windowed_dataset(
    series,
    input_window: int,
    forecast_horizon: int,
):
    """Slice a raw time series into (input window, target horizon) pairs.

    Args:
        series: array of shape (T, num_features), the raw weather time
            series.
        input_window: number of past timesteps fed to the LSTM.
        forecast_horizon: number of future timesteps to predict.

    Returns:
        Tuple (X, y) of arrays shaped for supervised training:
        X of shape (N, input_window, num_features),
        y of shape (N, forecast_horizon, num_features).
    """
    raise NotImplementedError


def train_model(
    model: nn.Module,
    train_loader,
    val_loader=None,
    num_epochs: int = 50,
    learning_rate: float = 1e-3,
    device: str = "cpu",
):
    """Train an LSTM forecaster with a standard supervised training loop.

    Args:
        model: a ForecastLSTM (or compatible) instance.
        train_loader: DataLoader yielding (X, y) batches.
        val_loader: optional DataLoader for validation-loss tracking.
        num_epochs: number of training epochs.
        learning_rate: optimizer learning rate (Adam).
        device: torch device string ("cpu" or "cuda").

    Returns:
        The trained model, and a dict of per-epoch train/val loss history.
    """
    raise NotImplementedError


def forecast_multistep(
    model: nn.Module,
    initial_window,
    num_steps: int,
    device: str = "cpu",
):
    """Roll a trained LSTM forward autoregressively to produce a multistep forecast.

    Args:
        model: trained ForecastLSTM.
        initial_window: array of shape (input_window, num_features), the
            most recent observed values to condition the forecast on.
        num_steps: number of future steps to forecast.
        device: torch device string.

    Returns:
        Array of shape (num_steps, num_features) with the forecast
        trajectory, for computing RMSE vs. lead time.
    """
    raise NotImplementedError
