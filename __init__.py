class NoPandasDataException(Exception):
    def __init__(self, passed_data) -> None:
        super().__init__()
        self.passed_data = passed_data
    
    def __str__(self) -> str:
        passed_type = type(self.passed_data)
        return f"{self.__module__} only supports operations on Pandas DataFrames. The one passed is of type {passed_type}"

