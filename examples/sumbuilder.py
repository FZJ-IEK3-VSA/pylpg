import os
import pandas as pd  # type: ignore

maindfs = None
# os.chdir("C:\\Work\\settlementresults\\result")
for file in os.listdir("."):

    if file.endswith(".csv"):
        print(file)
        df1 = pd.read_csv(file, header=None)
        newcolname = str(file).replace(".csv", "")
        print(newcolname)
        # df2 = df1.rename(columns={ "Electricity_HH1":newcolname})
        if len(df1.index) < 500000:
            continue
            # raise Exception("less than 500k rows")
        if maindfs is None:
            maindfs = df1
        else:
            maindfs[1] = maindfs[1] + df1[1]
        #   maindfs = maindfs.merge(df2, left_on=0,right_on=0)
assert maindfs is not None

maindfs = maindfs.drop(maindfs.columns[0], axis=1)
maindfs = maindfs.mul(60000)
# os.chdir("C:\\Work\\pylpg")
maindfs.to_csv("summed_up_t1.csv")
print("saved as summed_up_t1.csv")
