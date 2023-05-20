import pandas as pd
import numpy as np
from plotnine import *

class NoPandasDataException(Exception):
    def __init__(self, passed_data) -> None:
        super().__init__()
        self.passed_data = passed_data
    
    def __str__(self) -> str:
        passed_type = type(self.passed_data)
        return f"{self.__module__} only supports operations on Pandas DataFrames. The one passed is of type {passed_type}"
    

class Redundancy:

    def check_if_pandas_df(data):
        if data.__class__.__name__ == "DataFrame" and data.__module__ == "pandas.core.frame":
            return True
        else:
            return False

    def __init__(self, data: pd.DataFrame = pd.DataFrame()) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__data = data
        else:
            raise NoPandasDataException(data)
        
        self.__continuous, self.__categorical = None, None

    @property
    def data(self) -> pd.DataFrame:
        return self.__data
    
    @data.setter
    def data(self, data: pd.DataFrame) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__data = data
        else:
            raise NoPandasDataException(data)
        
    @property
    def categorical(self) -> pd.DataFrame:
        return self.__categorical
    
    @categorical.setter
    def categorical(self, data: pd.DataFrame) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__categorical = data
        else:
            raise NoPandasDataException(data)
    
    @property
    def continuous(self) -> pd.DataFrame:
        return self.__continuous
    
    @continuous.setter
    def continuous(self, data: pd.DataFrame) -> None:
        if Redundancy.check_if_pandas_df(data):
            self.__continuous = data
        else:
            raise NoPandasDataException(data)
        
    def split_data(self, k = 10, data = None):
        """Splits DataFrames into metric and categorical tables.
        The DataFrame is split based on the number of unique
        levels in each column. Having two separate DataFrames
        is useful for analysis and visualization.

        Parameters
        ----------
        data : pandas.DataFrame
        DataFrame to be split.
        k : int, default 10
        Cutoff threshold for classifying columns as metric or continuous.

        Returns
        -------
        df_conts : pandas.DataFrame
        DataFrame with only metric variables.
        df_cats : pandas.DataFrame
        DataFrame with only categorical variables.
        """
        if not Redundancy.check_if_pandas_df(data):
            if not Redundancy.check_if_pandas_df(self.data):
                raise NoPandasDataException
            else:
                data = self.data
        
        cats = []
        for col in data:
            if pd.unique(data[col]).size <= k:
                cats.append(col)
        df_conts = data.drop(cats, axis = 1)
        df_cats = data[cats]
        self.__continuous, self.__categorical = df_conts, df_cats
        return df_conts, df_cats


    




