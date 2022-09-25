from typing import Literal
import pandas as pd
import numpy as np
import datetime as dt
from options_backtest.modules.options_data import OptionsData


class Strategy:
    def __init__(
        self,
        index_data: pd.DataFrame,
        options_object: OptionsData,
        index: Literal["NIFTY", "BANKNIFTY"],
        nearest_premium: int = 100,
        close_time: dt.time = dt.time(15, 20),
    ) -> None:
        self.data = index_data
        self.close_time = close_time
        self.nearest_premium = nearest_premium
        self.options_obj = options_object
        self.index = index

        self.trade_book = pd.DataFrame(
            columns=[
                "instrument",
                "datetime",
                "price",
                "position_type",
                "expiry",
            ]
        )

        # Positions for the day
        self.entry_ce = []
        self.entry_pe = []

        self.exit_ce = []
        self.exit_pe = []

        # Statics for the day
        self.entry_price_ce = None
        self.entry_price_pe = None

        self.sl_ce = None
        self.sl_pe = None

        self.ticker_ce = None
        self.ticker_pe = None

    @staticmethod
    def is_expiry(candle: pd.Series) -> bool:
        return candle.name.date() == candle.expiry.date()

    @staticmethod
    def is_931(candle: pd.Series) -> bool:
        return candle.name.time() == dt.time(9, 31)

    def is_in_trade_range(self, candle: pd.Series) -> bool:
        return (candle.name.time() > dt.time(9, 31)) and (
            candle.name.time() <= self.close_time
        )

    def run_strategy(self):
        for c in range(16, len(self.data)):
            print(f"Current candle: {self.data.iloc[c].name}")

            if Strategy.is_expiry(self.data.iloc[c]):
                if Strategy.is_931(self.data.iloc[c]):
                    # Statics for the day
                    ce, pe = self.options_obj.get_strike_based_on_premium(
                        candle=self.data.iloc[c],
                        strike_list=self.data.iloc[c].spread,
                        premium=self.nearest_premium,
                        index=self.index,
                    )
                    entry_price_ce = np.round(ce.close / 2, 2)
                    entry_price_pe = np.round(pe.close / 2, 2)
                    sl_ce = ce.close
                    sl_pe = pe.close
                    ticker_ce = ce.name
                    ticker_pe = pe.name

                elif self.is_in_trade_range(self.data.iloc[c]):
                    ce_n = self.options_obj.read_strike_data(
                        f"{ticker_ce}.csv", self.data.iloc[c].name
                    ).iloc[-1]

                    pe_n = self.options_obj.read_strike_data(
                        f"{ticker_pe}.csv", self.data.iloc[c].name
                    ).iloc[-1]

                    # Entry
                    if (
                        (self.data.iloc[c].name.time() < self.close_time)
                        and (not self.entry_ce)
                        and (ce_n.close <= entry_price_ce)
                    ):
                        self.entry_ce.append(
                            (
                                ticker_ce,
                                self.data.iloc[c].name,
                                ce_n.close,
                                "Entry",
                                self.data.iloc[c].expiry,
                            )
                        )
                        self.trade_book.loc[len(self.trade_book), :] = list(
                            *self.entry_ce
                        )

                    if (
                        (self.data.iloc[c].name.time() < self.close_time)
                        and (not self.entry_pe)
                        and (pe_n.close <= entry_price_pe)
                    ):
                        self.entry_pe.append(
                            (
                                ticker_pe,
                                self.data.iloc[c].name,
                                pe_n.close,
                                "Entry",
                                self.data.iloc[c].expiry,
                            )
                        )
                        self.trade_book.loc[len(self.trade_book), :] = list(
                            *self.entry_pe
                        )

                    # SL
                    if (
                        (not not self.entry_ce)
                        and (not self.exit_ce)
                        and (ce_n.close >= sl_ce)
                    ):
                        self.exit_ce.append(
                            (
                                ticker_ce,
                                self.data.iloc[c].name,
                                -ce_n.close,
                                "SL",
                                self.data.iloc[c].expiry,
                            )
                        )
                        self.trade_book.loc[len(self.trade_book), :] = list(
                            *self.exit_ce
                        )

                    if (
                        (not not self.entry_pe)
                        and (not self.exit_pe)
                        and (pe_n.close >= sl_pe)
                    ):
                        self.exit_pe.append(
                            (
                                ticker_pe,
                                self.data.iloc[c].name,
                                -pe_n.close,
                                "SL",
                                self.data.iloc[c].expiry,
                            )
                        )
                        self.trade_book.loc[len(self.trade_book), :] = list(
                            *self.exit_pe
                        )

                    # Time
                    if self.data.iloc[c].name.time() == self.close_time:
                        # Close open positions
                        if (not not self.entry_ce) and (not self.exit_ce):
                            self.exit_ce.append(
                                (
                                    ticker_ce,
                                    self.data.iloc[c].name,
                                    -ce_n.close,
                                    "Time",
                                    self.data.iloc[c].expiry,
                                )
                            )
                            self.trade_book.loc[
                                len(self.trade_book), :
                            ] = list(*self.exit_ce)
                        if (not not self.entry_pe) and (not self.exit_pe):
                            self.exit_pe.append(
                                (
                                    ticker_pe,
                                    self.data.iloc[c].name,
                                    -pe_n.close,
                                    "Time",
                                    self.data.iloc[c].expiry,
                                )
                            )
                            self.trade_book.loc[
                                len(self.trade_book), :
                            ] = list(*self.exit_pe)

                        # Reset variables
                        self.entry_ce.clear()
                        self.entry_pe.clear()
                        self.exit_ce.clear()
                        self.exit_pe.clear()
                        entry_price_ce = None
                        entry_price_pe = None

                        sl_ce = None
                        sl_pe = None

                        ticker_ce = None
                        ticker_pe = None
                else:
                    print(
                        f"{self.data.iloc[c].name} It is beyond trading range"
                    )
