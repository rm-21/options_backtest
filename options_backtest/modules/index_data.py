import datetime as dt
from typing import Literal

import pandas as pd
from options_backtest.config.models import STRIKE_SPREAD


class IndexData:
    def __init__(
        self, data_loc: str, start_date: str, end_date: str, expiry_map: dict
    ) -> None:
        self.data_loc = data_loc
        self.start_date = start_date
        self.end_date = end_date
        self.expiry_map = expiry_map

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

        # Options info
        data["atm_strike"] = data["close"].apply(
            lambda c: IndexData._get_atm_strike(c, "BANKNIFTY")
        )

        data["spread"] = data["atm_strike"].apply(
            lambda c: IndexData._get_strike_either_side(c, "BANKNIFTY", 7)
        )

        expiries = pd.DataFrame(data.index)["datetime"].apply(
            lambda c: IndexData._get_expiry(c, expiry_map=self.expiry_map)
        )

        data["expiry"] = expiries.values

        return data

    @staticmethod
    def _fetch_spread(index: Literal["NIFTY", "BANKNIFTY"]) -> int:
        if index == "NIFTY":
            return STRIKE_SPREAD.NIFTY.value
        elif index == "BANKNIFTY":
            return STRIKE_SPREAD.BANKNIFTY.value
        else:
            raise AttributeError(
                "index can only have ['NIFTY', 'BANKNIFTY'] values."
            )

    @staticmethod
    def _get_atm_strike(
        value: float, index: Literal["NIFTY", "BANKNIFTY"]
    ) -> int:
        strike_spread = IndexData._fetch_spread(index=index)

        if (value % strike_spread) >= int(strike_spread / 2):
            return int(value - (value % strike_spread) + strike_spread)
        else:
            return int(value - (value % strike_spread))

    @staticmethod
    def _get_strike_either_side(
        atm_strike: int, index: Literal["NIFTY", "BANKNIFTY"], num: int = 5
    ) -> list:
        strike_list = []
        strike_spread = IndexData._fetch_spread(index=index)
        start = atm_strike - (num * strike_spread)
        for s in range(num * 2 + 1):
            strike_list.append(start)
            start += strike_spread

        return strike_list

    @staticmethod
    def _get_expiry(today_date: dt.datetime, expiry_map: dict) -> dt.datetime:
        expiry_dates = list(expiry_map.values())
        coming_expiry_idx = [
            _[0] for _ in enumerate(expiry_dates) if _[1] > today_date
        ][0]
        expiry = expiry_dates[coming_expiry_idx]
        return expiry
