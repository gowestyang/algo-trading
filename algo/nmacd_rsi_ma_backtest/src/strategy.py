"""
Strategy

Ref: https://www.youtube.com/watch?v=fT4jb-I5zYc&t=8s

Long Signal:
1. NMACD cross over
2. RSI cross over
3. At the bar of RSI cross over, the close price is above SMA
"""

import numpy as np
from src.defs import BROKER
from src.notifications import log_order, log_trade
from backtrader_bokeh import bt


INSTRUMENT = "EUR_USD"
DIGITS = BROKER.PRICE_DIGITS[INSTRUMENT]
SPREAD = BROKER.SPREAD[INSTRUMENT]


class MyStrategy(bt.Strategy):
    params = (
        ("macd_fast_period", 13),
        ("macd_slow_period", 21),
        ("macd_signal_period", 9),  # signal / trigger
        # ('macd_normalize_period', 50),
        ("rsi_period", 21),
        ("rsi_ma_period", 55),
        ("ma_period", 13),
        ("high_low_period", 8),
        # ('atr_period', 115),
        ("rrr", 1),  # reward-risk-ratio = take-profit-distance / stop-loss-distance
        ("sl_pct", 1),  # stop-loss pct = stop-loss-amount / total-cash-amount
    )

    def __init__(self):
        # indicators
        self.sma = bt.indicators.SimpleMovingAverage(period=self.params.ma_period)

        self.macd = bt.indicators.MACD(
            period_me1=self.params.macd_fast_period,
            period_me2=self.params.macd_slow_period,
            period_signal=self.params.macd_signal_period,
        )

        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        self.rsi_ma = bt.indicators.SimpleMovingAverage(self.rsi, period=self.params.rsi_ma_period)
        self.rsi_ma.plotinfo.plotmaster = self.rsi  # plot rsi_ma in the rsi chart

        # self.atr = bt.indicators.AverageTrueRange(period=self.params.atr_period)

        self.recent_high = bt.indicators.Highest(self.data.high, period=self.params.high_low_period, plot=False)
        self.recent_low = bt.indicators.Lowest(self.data.low, period=self.params.high_low_period, plot=False)

        # signals
        self.macd_crossover = bt.indicators.CrossOver(
            self.macd.macd, self.macd.signal, plot=False
        )  # 0: no cross-over | 1: cross-up | -1 : cross-down
        self.rsi_crossover = bt.indicators.CrossOver(
            self.rsi, self.rsi_ma, plot=False
        )  # 0: no cross-over | 1: cross-up | -1 : cross-down
        self.had_macd_cross = 0  # 0: no signal | 1: cross above | -1: cross below
        self.signal = 0  # 0: no signal | 1: long | -1: short

        # to prevent tirgger trade immediately after close in the same bar
        self.prev_len = 0  # len(self) will increase by 1 after every compressed bar
        self.allow_trigger = True

        # prices
        self.stop_loss = None
        self.take_profit = None

        # trade log
        self.trade_log = []
        self.is_trade_open = False
        self.trade_num = 0

        # others
        self.close_price = None
        self.order = None  # to keep track whether there is an open order

    def update_signal(self):
        if self.macd_crossover[0] != 0:
            self.had_macd_cross = self.macd_crossover[0]

        if self.had_macd_cross == 1:
            if (self.rsi_crossover[0] == 1) & (self.data.close[0] > self.sma[0]):
                self.signal = 1
            else:
                self.signal = 0

        if self.had_macd_cross == -1:
            if (self.rsi_crossover[0] == -1) & (self.data.close[0] < self.sma[0]):
                self.signal = -1
            else:
                self.signal = 0

    def next(self):
        #### trouble shooting ####
        # global g1
        # g1 = self.atr
        # self.log(self.atr[0])
        ####

        # update signal
        self.update_signal()

        if len(self) > self.prev_len:
            self.allow_trigger = True
            self.prev_len = len(self)

        # do not open new trade if there is pending order / open trade / trigger not allowed
        if self.order or self.position or (not self.allow_trigger):
            return

        self.close_price = self.data.close[0]
        self.leverage = self.broker.getcommissioninfo(self.data).get_leverage()

        if self.signal == 1:
            self.log(f"BUY MKT ORDER TRIGGERED.")
            sl = self.round(self.recent_low[0] + SPREAD)
            sl_dist = abs(self.close_price - sl)
            tp_dist = sl_dist * self.params.rrr
            tp = self.round(self.close_price + tp_dist)

            size = self.calc_size(sl_dist)

            self.stop_loss = sl
            self.take_profit = tp
            self.order = self.buy_bracket(
                size=size,
                exectype=bt.Order.Market,
                stopprice=self.stop_loss,
                stopexec=bt.Order.Stop,
                limitprice=self.take_profit,
                limitexec=bt.Order.Limit,
            )
        if self.signal == -1:
            self.log(f"SELL MKT ORDER TRIGGERED.")
            sl = self.round(self.recent_high[0] + SPREAD)
            sl_dist = abs(self.close_price - sl)
            tp_dist = sl_dist * self.params.rrr
            tp = self.round(self.close_price - tp_dist)

            size = self.calc_size(sl_dist)

            self.stop_loss = sl
            self.take_profit = tp
            self.order = self.sell_bracket(
                size=size,
                exectype=bt.Order.Market,
                stopprice=self.stop_loss,
                stopexec=bt.Order.Stop,
                limitprice=self.take_profit,
                limitexec=bt.Order.Limit,
            )

    def notify_order(self, order: bt.order.Order) -> None:
        log_order(order=order, digits=DIGITS, log_func=self.log)

        # log executed order
        if order.status == order.Completed:
            self.is_trade_open = not self.is_trade_open
            dt = self.data.datetime.datetime(0).strftime("%Y-%m-%d %H:%M:%S")
            direction = "BUY" if order.isbuy() else "SELL"

            if self.is_trade_open:
                # the order execution opened a new trade
                self.trade_num += 1
                self.trade_log.append(
                    {
                        "datetime": dt,
                        "trade_num": self.trade_num,
                        "type": "open",
                        "direction": direction,
                        "last_close_price": self.close_price,
                        "created_price": order.created.price,
                        "executed_price": order.executed.price,
                        "stop_lose_price": self.stop_loss,
                        "take_profit_price": self.take_profit,
                    }
                )
            else:
                # the order execution closed an existing trade
                self.trade_log.append(
                    {
                        "datetime": dt,
                        "trade_num": self.trade_num,
                        "type": "close",
                        "direction": direction,
                        "last_close_price": self.close_price,
                        "created_price": order.created.price,
                        "executed_price": order.executed.price,
                        "stop_lose_price": np.nan,
                        "take_profit_price": np.nan,
                    }
                )

        # no pending order unless partially filled
        if order.status != order.Partial:
            self.order = None

    def notify_trade(self, trade: bt.trade.Trade) -> None:
        self.allow_trigger = False
        log_trade(trade=trade, digits=DIGITS, log_func=self.log)

    def start(self) -> None:
        self.log(
            f"STRATEGY START: value = {round(self.broker.getvalue(), DIGITS)}, cash = {round(self.broker.getcash(), DIGITS)}.",
            with_dt=False,
        )

    def stop(self) -> None:
        self.log(
            f"STRATEGY COMPLETE: value = {round(self.broker.getvalue(), DIGITS)}, cash = {round(self.broker.getcash(), DIGITS)}."
        )

    def log(self, txt: str, with_dt: bool = True) -> None:
        if with_dt:
            dt = self.data.datetime.datetime(0)
            txt = f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] {txt}"
        print(txt)

    def round(self, price: float) -> float:
        return round(price, DIGITS)

    def calc_size(self, sl_dist):
        cash = self.broker.getcash()
        sl_pct = self.params.sl_pct
        unit = BROKER.POSITION_UNIT[INSTRUMENT]
        return ((cash * sl_pct / 100 / sl_dist) // unit) * unit
