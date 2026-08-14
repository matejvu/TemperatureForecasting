"""Plots for the real-data pipeline: station series and RMSE vs. lead time."""

import matplotlib.pyplot as plt
import pandas as pd

# Must match STATION_NAME in fetch_data.py — kept as a plain constant here
# (instead of importing it from fetch_data) so this script doesn't need
# the openmeteo_requests/requests_cache/retry_requests dependencies.
STATION_NAME = "petnica"


def load_station_csv(path: str) -> pd.DataFrame:
    """Load the CSV produced by real_data/fetch_data.py, indexed by timestamp.

    Args:
        path: path to the "<station>_data.csv" file.

    Returns:
        DataFrame indexed by timestamp (parsed as datetime).
    """
    return pd.read_csv(path, index_col=0, parse_dates=True)


def plot_temperature_vs_date(
    df: pd.DataFrame,
    column: str = "temperature_2m",
    save_path: str = None,
):
    """Plot 2m temperature vs. date.

    Args:
        df: DataFrame indexed by timestamp, with a temperature column
            (as produced by real_data/fetch_data.py, e.g. "temperature_2m").
        column: name of the temperature column to plot.
        save_path: optional file path to save the figure to; if None,
            the figure is shown interactively.
    """
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df.index, df[column], linewidth=0.8, color="tab:red")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("2m Temperature vs. Date")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path)
        plt.close(fig)
    else:
        plt.show()


def plot_surface_pressure_vs_date(
    df: pd.DataFrame,
    column: str = "surface_pressure",
    save_path: str = None,
):
    """Plot surface pressure vs. date.

    Args:
        df: DataFrame indexed by timestamp, with a surface pressure
            column (as produced by real_data/fetch_data.py, e.g.
            "surface_pressure").
        column: name of the surface pressure column to plot.
        save_path: optional file path to save the figure to; if None,
            the figure is shown interactively.
    """
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df.index, df[column], linewidth=0.8, color="tab:blue")
    ax.set_xlabel("Date")
    ax.set_ylabel("Surface pressure (hPa)")
    ax.set_title("Surface Pressure vs. Date")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path)
        plt.close(fig)
    else:
        plt.show()


def plot_series_vs_time(
    truth: pd.DataFrame,
    nwp_forecasts: pd.DataFrame = None,
    save_path: str = None,
):
    """Plot each weather variable vs. time, optionally overlaying an NWP forecast at one lead time.

    Args:
        truth: DataFrame of ERA5 truth values, indexed by timestamp.
        nwp_forecasts: optional DataFrame of archived NWP forecast values
            to overlay.
        save_path: optional file path to save the figure to; if None,
            the figure is shown interactively.
    """
    raise NotImplementedError


def plot_rmse_vs_lead_time(
    rmse_by_method: dict,
    save_path: str = None,
):
    """Plot RMSE vs. lead time for all forecasting methods on one set of axes.

    This is the headline result: LSTM, archived NWP, persistence, and
    climatology curves, framed per README.md as "how much of the gap to
    the physics pipeline can a lightweight data-driven model close."

    Args:
        rmse_by_method: dict mapping method name -> array of RMSE values
            at each lead time (output of
            real_data.evaluate.evaluate_all_methods).
        save_path: optional file path to save the figure to; if None,
            the figure is shown interactively.
    """
    raise NotImplementedError


if __name__ == "__main__":
    csv_path = f"real_data/{STATION_NAME}_data.csv"
    df = load_station_csv(csv_path)

    plot_temperature_vs_date(
        df, save_path=f"real_data/{STATION_NAME}_temperature.png"
    )
    plot_surface_pressure_vs_date(
        df, save_path=f"real_data/{STATION_NAME}_surface_pressure.png"
    )
    print(f"Saved plots to real_data/{STATION_NAME}_temperature.png "
          f"and real_data/{STATION_NAME}_surface_pressure.png")
