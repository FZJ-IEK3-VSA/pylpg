from datetime import datetime, time, timedelta

import numpy as np
import pandas as pd  # type: ignore
from matplotlib import dates as mdates  # type: ignore
from matplotlib import pyplot as plt
from matplotlib import ticker


def carpet_plot(data: pd.DataFrame | pd.Series, title: str = "", vmin=None, vmax=None):
    """
    Shows a carpet plot of the data (expects data for a whole year)

    :param data: a time series for one year
    :type data: pd.DataFrame | pd.Series
    :param title: the title for the diagram, defaults to ""
    :type title: str, optional
    :param vmin: minimum value for the scale, defaults to None
    :param vmax: maximum value for the scale, defaults to None
    """
    # get the list of days in the time frame of the data
    dates = pd.date_range(data.index[0].date(), data.index[-1].date(), freq="d")
    # assume a fixed resolution
    resolution: timedelta = data.index[1] - data.index[0]
    values_per_day = timedelta(1) // resolution
    array = np.full((values_per_day, len(dates)), np.nan)
    for i in range(array.shape[1]):
        date_ = datetime.combine(dates[i], time())
        for j in range(array.shape[0]):
            dt = date_ + resolution * j
            if dt in data.index:
                array[j, i] = data[dt]

    # initialize figure
    fig = plt.figure()
    ax: plt.Axes = fig.add_subplot(1, 1, 1)
    # calculate a datetimeindex with one more day
    x = dates.union(pd.date_range(dates[-1] + dates.freq, periods=1, freq=dates.freq))
    y = np.linspace(0, 24, values_per_day + 1)

    color_mesh = ax.pcolormesh(x, y, array, cmap="jet", vmin=vmin, vmax=vmax)

    # draw major ticks, but label minor ticks to get put each label between two major ticks
    date_formatter = mdates.DateFormatter("%b")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=16))
    ax.xaxis.set_minor_formatter(date_formatter)
    # remove the minor ticks
    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment("center")

    year = data.index[len(data.index) // 2].year
    ax.xaxis.set_label_text(year)
    ax.yaxis.set_label_text("Time [h]")
    ax.invert_yaxis()
    ax.set_title(title)
    cbar = fig.colorbar(color_mesh)
    cbar.ax.set_ylabel("Electric Load [kWh]")
    fig.tight_layout()
    fig.show()
    