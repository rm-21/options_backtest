import pandas as pd
import datetime as dt
import os
from typing import Literal


class OptionsData:
    def __init__(self, data_loc: str, expiry_map: dict) -> None:
        self.data_loc = data_loc
        self.expiry_map = expiry_map

        self.options_mapper = self._create_options_data_mapper()

    def _create_options_data_mapper(self) -> pd.DataFrame:
        options_files = pd.DataFrame(
            os.listdir(self.data_loc), columns=["file_name"]
        )
        options_files["index"] = options_files["file_name"].str[:9]
        options_files["type"] = options_files["file_name"].str[-6:-4]
        options_files["strike"] = (
            options_files["file_name"].str[-11:-6].astype(int)
        )
        options_files["expiry"] = options_files["file_name"].str[9:].str[:-11]
        options_files = options_files[
            options_files.expiry.isin(self.expiry_map.keys())
        ]
        options_files["expiry_date"] = options_files["expiry"].map(
            self.expiry_map
        )
        options_files = options_files.sort_values(
            by=["expiry_date", "strike", "type"]
        ).reset_index(drop=True)
        return options_files

    def read_strike_data(self, file_name: str, datetime: dt.datetime):
        strike_data = pd.read_csv(f"{self.data_loc}/{file_name}")

        # Refactor columns
        strike_data.columns = (
            strike_data.columns.str.lower().str.lstrip().str.rstrip()
        )

        # Merge date and time
        strike_data["datetime"] = pd.to_datetime(
            strike_data["date"] + " " + strike_data["time"]
        )
        strike_data = strike_data.drop(columns=["date", "time"]).set_index(
            "datetime", drop=True
        )
        strike_data = strike_data.resample("1min").ffill()
        strike_data = strike_data[
            datetime
            - dt.timedelta(minutes=5) : datetime
            - dt.timedelta(minutes=1)
        ]
        return strike_data

    def get_option_file(
        self,
        expiry_date: dt.datetime,
        index: Literal["NIFTY", "BANKNIFTY"],
        type_: Literal["CE", "PE"],
        strike: int,
    ):
        expiry_filter = self.options_mapper["expiry_date"] == expiry_date
        index_filter = self.options_mapper["index"] == index
        type_filter = self.options_mapper["type"] == type_
        strike_filter = self.options_mapper["strike"] == strike
        file_name = self.options_mapper[
            expiry_filter & index_filter & type_filter & strike_filter
        ]["file_name"].values[0]
        return file_name

    def get_strike_based_on_premium(
        self,
        candle: pd.Series,
        strike_list: list,
        premium: int,
        index: Literal["NIFTY", "BANKNIFTY"],
    ):
        ce_data = []
        pe_data = []

        for strike in strike_list:
            # CE File
            ce_file = self.get_option_file(
                expiry_date=candle.expiry,
                index=index,
                type_="CE",
                strike=strike,
            )

            try:
                ce_read = self.read_strike_data(
                    file_name=ce_file,
                    datetime=candle.name,
                ).iloc[-1]
                ce_tmp = ce_read.to_list()
                ce_tmp.append(ce_read.name)
                ce_data.append(ce_tmp)
            except IndexError as e:
                print(f"{e}: Skipping file {ce_file}")

            # PE File
            pe_file = self.get_option_file(
                expiry_date=candle.expiry,
                index=index,
                type_="PE",
                strike=strike,
            )

            try:
                pe_read = self.read_strike_data(
                    file_name=pe_file,
                    datetime=candle.name,
                ).iloc[-1]
                pe_tmp = pe_read.to_list()
                pe_tmp.append(pe_read.name)
                pe_data.append(pe_tmp)
            except IndexError as e:
                print(f"{e}: Skipping file {pe_file}")

        ce_data = pd.DataFrame(
            data=ce_data,
            columns=[
                "strike",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "datetime",
            ],
        ).set_index("strike", drop=True)

        pe_data = pd.DataFrame(
            data=pe_data,
            columns=[
                "strike",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "datetime",
            ],
        ).set_index("strike", drop=True)

        ce_closest_to_premium = ce_data.iloc[
            (ce_data["close"] - premium).abs().argsort()[0], :
        ]
        pe_closest_to_premium = pe_data.iloc[
            (pe_data["close"] - premium).abs().argsort()[0], :
        ]
        return ce_closest_to_premium, pe_closest_to_premium
