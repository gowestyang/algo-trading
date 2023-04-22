import os
import pandas as pd
from datetime import datetime
from src.defs import PRICE_DIGITS
from src.utils import logger, load_oanda_parquet
from src.notifications import log_order, log_trade

# from backtrader_bokeh import bt
import backtrader as bt

logger.setLevel(10)  # debug

INSTRUMENT = "EUR_USD"
DIGITS = PRICE_DIGITS[INSTRUMENT]


class MyStrategy(bt.Strategy):
    params = (
        ("macd_fast_period", 13),
        ("macd_slow_period", 21),
        ("macd_signal_period", 9),  # signal / trigger
        ("macd_normalize_period", 50),
        ("rsi_period", 21),
        ("rsi_ma_period", 55),
        ("ma_period", 13),
        ("atr_period", 100),
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
        self.rsi_ma.plotinfo.plotmaster = self.rsi

        self.atr = bt.indicators.AverageTrueRange(period=self.params.atr_period)

        # signals
        self.macd_crossover = bt.indicators.CrossOver(
            self.macd.macd, self.macd.signal, plot=False
        )  # 0: no cross-over | 1: cross-up | -1 : cross-down
        self.rsi_crossover = bt.indicators.CrossOver(
            self.rsi, self.rsi_ma, plot=False
        )  # 0: no cross-over | 1: cross-up | -1 : cross-down
        self.sig_macd_cross = 0  # 0: no signal | 1: cross above | -1: cross below
        self.signal = 0  # 0: no signal | 1: long | -1: short

        # prices
        self.stop_loss = None
        self.take_profit = None

        # others
        self.close_price = None
        self.order = None

    def update_signal(self):
        if self.macd_crossover[0] != 0:
            self.sig_macd_cross = self.macd_crossover[0]

        if self.sig_macd_cross == 1:
            if (self.rsi_crossover[0] == 1) & (self.data.close[0] > self.sma[0]):
                self.signal = 1
            else:
                self.signal = 0

        if self.sig_macd_cross == -1:
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

        # if there is a pending order, do not send a 2nd one
        if self.order:
            return

        # update signal
        self.update_signal()

        # apply signal if not in position
        if not self.position:
            if self.signal == 1:
                self.log(f"BUY MKT ORDER TRIGGERED.")
                self.stop_loss = round(self.data.close[0] - self.atr[0], DIGITS)
                self.take_profit = round(self.data.close[0] + self.atr[0], DIGITS)
                self.order = self.buy_bracket(
                    size=None,
                    exectype=bt.Order.Market,
                    stopprice=self.stop_loss,
                    stopexec=bt.Order.Stop,
                    limitprice=self.take_profit,
                    limitexec=bt.Order.Limit,
                )
            if self.signal == -1:
                self.log(f"SELL MKT ORDER TRIGGERED.")
                self.stop_loss = round(self.data.close[0] + self.atr[0], DIGITS)
                self.take_profit = round(self.data.close[0] - self.atr[0], DIGITS)
                self.order = self.sell_bracket(
                    size=None,
                    exectype=bt.Order.Market,
                    stopprice=self.stop_loss,
                    stopexec=bt.Order.Stop,
                    limitprice=self.take_profit,
                    limitexec=bt.Order.Limit,
                )

    def notify_order(self, order: bt.order.Order) -> None:
        log_order(order=order, digits=DIGITS, log_func=self.log)

        # no pending order unless partially filled
        if order.status != order.Partial:
            self.order = None

    def notify_trade(self, trade: bt.trade.Trade) -> None:
        log_trade(trade=trade, digits=DIGITS, log_func=self.log)

    def start(self):
        self.log(
            f"STRATEGY START. value = {round(self.broker.getvalue(), DIGITS)}, cash = {round(self.broker.getcash(), DIGITS)}.",
            with_dt=False,
        )

    def stop(self):
        self.log(
            f"STRATEGY COMPLETE. value = {round(self.broker.getvalue(), DIGITS)}, cash = {round(self.broker.getcash(), DIGITS)}."
        )

    def log(self, txt, with_dt=True):
        if with_dt:
            dt = self.data.datetime.datetime(0)
            txt = f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] {txt}"
        print(txt)


DATA_FILE = "oanda_EUR_USD_H1_2022-12-19_2022-12-31.parquet.gz"

# initialize
cerebro = bt.Cerebro()
cerebro.broker.setcash(1000)
cerebro.broker.setcommission(commission=0.0)

# add data
df = load_oanda_parquet(DATA_FILE)

data = bt.feeds.PandasData(
    dataname=df,
    name="EUR_USD_H1",
)

cerebro.adddata(data)

# add strategy
cerebro.addstrategy(MyStrategy)

# add sizer
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

cerebro.run()

cerebro.plot(style="candles", barup="green", bardown="red")
