import pandas as pd


class IndexData:
    def __init__(self, data_loc: str, start_date: str, end_date: str) -> None:
        self.data_loc = data_loc
        self.start_date = start_date
        self.end_date = end_date

        self.data = self._clean_data()

    def _clean_data(self) -> None:
        data = pd.read_csv(self.data_loc)

        # Refactor columns
        data.columns = data.columns.str.lower().str.lstrip().str.rstrip()

        # Merge date and time
        data["datetime"] = pd.to_datetime(data["date"] + " " + data["time"])
        data = data.drop(columns=["date", "time", "volume"]).set_index(
            "datetime", drop=True
        )

        # Data in Range
        data = data[self.start_date : self.end_date]
        return data
