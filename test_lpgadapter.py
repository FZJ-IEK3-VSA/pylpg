from lpgadapter import *
import pandas  # type: ignore
import pathlib


def test_housejob_example() -> None:
    le: LPGExecutor = LPGExecutor()
    path = pathlib.Path(__file__).parent.absolute()
    random.seed(2)
    df: pandas.DataFrame = le.excute_lpg_locally(2020, 2, 2, path, startdate="01.01.2020", enddate="01.03.2020", transportation=True)
    df.to_csv(r'lpgexport.csv', index=True, sep=";")
    print("successfully exportet dataframe to lpgexport.csv")

if __name__ == "__main__":
    test_housejob_example()