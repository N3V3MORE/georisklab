import numpy as np
import pandas as pd

from georisklab.visualization.plots import plot_gpr_timeseries


def test_plot_gpr_timeseries_uses_main_shock_by_default():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=3, freq="MS"),
            "gpr_global_z": [10.0, 20.0, 30.0],
            "gpr_change_z": [-1.0, 0.0, 1.0],
        }
    )

    figure = plot_gpr_timeseries(df)
    y_values = figure.axes[0].lines[0].get_ydata()

    np.testing.assert_allclose(y_values, df["gpr_change_z"])
    assert figure.axes[0].get_title() == "Global geopolitical risk shock"
