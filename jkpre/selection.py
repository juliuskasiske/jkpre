import pandas as pd
import numpy as np
from jkpre import NoPandasDataException

class Redundancy:

    def check_if_pandas_df(data):
        if data.__module__ == "pandas.core.frame" and data.__class__.__name__ == "DataFrame":
            return True
        else:
            return False

    def __init__(self, data: pd.DataFrame = None) -> None:
        if self.check_if_pandas_df(data):
            self.__data = data
        else:
            raise NoPandasDataException

    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    
    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        if self.check_if_pandas_df(data):
            self.__data = data
        else:
            raise NoPandasDataException
    



