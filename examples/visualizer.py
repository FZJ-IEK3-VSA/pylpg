import os
import pandas as pd  # type: ignore


def plotdf(myseries, filename):
    ax = myseries.plot(figsize=(32, 20))
    fig = ax.get_figure()
    fig.savefig(filename)
    fig.clear()


df1 = pd.read_csv("summed_up_t1.csv", header=None)
df1.columns = ["idx", "val"]
df_r = df1.copy()
plotdf(df_r["val"].rolling(365 * 24).median(), "myplot.png")
dayoffset = 31 + 29 + 31 + 5
dfjan = df1[1440 * dayoffset : 1440 * (dayoffset + 7)]["val"]

plotdf(dfjan, "myplotjan.png")
