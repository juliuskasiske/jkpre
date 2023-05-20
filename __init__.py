class NoPandasDataException(Exception):
    def __init__(self) -> None:
        super().__init__()
    
    def __str__(self) -> str:
        return f"{self.__module__} only supports operations on Pandas DataFrames"

