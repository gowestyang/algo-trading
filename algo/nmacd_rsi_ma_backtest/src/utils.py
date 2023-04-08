from typing import Tuple
import logging
import pandas as pd

# logger
LOGGING_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"
LOGGING_LEVEL = logging.INFO
logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def load_oanda_parquet(file:str, start_time:str=None, end_time:str=None) -> Tuple[pd.DataFrame]:
    """Load saved OANDA parquest"""

    INPUT_COLS = ["time", "volume", "bid_o", "bid_h", "bid_l", "bid_c", "ask_o", "ask_h", "ask_l", "ask_c"]

    df = pd.read_parquet(file)

    # verify columns
    missing_cols = [c for c in INPUT_COLS if c not in df.columns]
    if len(missing_cols) > 0:
        logger.error(f"Missing columns: {missing_cols}.")

    df["datetime"] = pd.to_datetime(df["time"])

    if start_time is not None:
        df = df[df["datetime"] >= start_time].reset_index(drop=True)
    if end_time is not None:
        df = df[df["datetime"] < end_time].reset_index(drop=True)

    # use mid prices as OHLC
    df["open"] = (df["bid_o"] + df["ask_o"]) / 2
    df["high"] = (df["bid_h"] + df["ask_h"]) / 2
    df["low"] = (df["bid_l"] + df["ask_l"]) / 2
    df["close"] = (df["bid_c"] + df["ask_c"]) / 2

    cols = ["datetime", "open", "high", "low", "close", "volume"]
    df = df[cols].copy()
    logger.debug(f"Loaded data has {len(df)} rows, from {df['datetime'].min()} to {df['datetime'].max()}.")
    df = df[cols].copy().set_index("datetime", verify_integrity=True)

    return df
