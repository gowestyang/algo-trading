import os
import pandas as pd
from datetime import datetime
from src.utils import logger, load_oanda_parquet

# from backtrader_bokeh import bt
import backtrader as bt

os.environ["BOKEH_ALLOW_WS_ORIGIN"] = "0lj9hh483va927cadklatiu5affjj5cn3b349he4cl71d36qc4p6"

logger.setLevel(10)  # debug

DATA_FILE = "oanda_EUR_USD_H1_2022-12-19_2022-12-31.parquet.gz"

df = load_oanda_parquet(DATA_FILE)

data = bt.feeds.PandasData(
    dataname=df,
    name="EUR_USD_H1",
)


class RSI_MA(bt.Indicator):
    params = (
        ("period", 14),
        ("ma_period", 10),
    )
    lines = ("rsi", "rsi_ma")
    plotinfo = dict(subplot=True, plotlinelabels=True, plotmaster=bt.indicators.RSI())
    plotlines = dict(rsi=dict(ls="-", linewidth=1.5), rsi_ma=dict(ls="--", linewidth=1.5))

    def __init__(self):
        self.lines.rsi = bt.indicators.RSI(period=self.params.period)
        self.lines.ma_rsi = bt.indicators.SimpleMovingAverage(
            self.lines.rsi, period=self.params.ma_period, plotforce=True
        )


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
        self.macd_crossover = bt.indicators.CrossOver(
            self.macd.macd, self.macd.signal, plot=False
        )  # 0: no cross-over | 1: cross-up | -1 : cross-down
        # self.macd_norm = bt.indicators.NormalizedMovingAverage(self.macd.histo, period=self.params.macd_normalize_period)

        self.rsi = RSI_MA(period=self.params.rsi_period, ma_period=self.params.rsi_ma_period)
        # self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        # self.rsi_ma = bt.indicators.SimpleMovingAverage(self.rsi, period=self.params.rsi_ma_period)
        # self.rsi_crossover = bt.indicators.CrossOver(self.rsi, self.rsi_ma) # 0: no cross-over | 1: cross-up | -1 : cross-down

        self.atr = bt.indicators.AverageTrueRange(period=self.params.atr_period)

        # signals
        self.sig_macd_cross = 0  # 0: no signal | 1: cross above | -1: cross below
        self.signal = 0  # 0: no signal | 1: long | -1: short

        self.order = None
        self.buyprice = None
        self.buycomm = None

    def update_signal(self):
        if self.macd_crossover[0] in (-1, 1):
            self.sig_macd_cross = self.macd_crossover[0]

        if self.sig_macd_cross == 1:
            # if (self.rsi_crossover[0]==1) & (self.data.close[0] > self.sma[0]):
            if self.data.close[0] > self.sma[0]:
                self.signal = 1
            else:
                self.signal = 0

        if self.sig_macd_cross == -1:
            # if (self.rsi_crossover[0]==-1) & (self.data.close[0] < self.sma[0]):
            if self.data.close[0] < self.sma[0]:
                self.signal = -1
            else:
                self.signal = 0

    def next(self):
        #### troubleshootgin ####
        # global g1
        # g1 = self.rsi
        # self.log(f"macd_crossover = {self.macd_crossover[0]}")
        ####

        # if there is a pending order, do not send a 2nd one
        if self.order:
            return

        # update signal
        self.update_signal()

        if self.signal != 0:
            self.log({f"signal = {self.signal}"})

        # apply signal if not in position
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.log(f"BUY CREATE, {self.data.close[0]:.6f}")
                self.order = self.buy()

        else:
            if self.data.close[0] < self.sma[0]:
                self.log(f"SELL CREATE, {self.data.close[0]:.6f}")
                self.order = self.sell()

    def notify_order(self, order: bt.order.Order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log_order(order)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log_order(order)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade: bt.trade.Trade):
        if not trade.isclosed:
            return
        self.log(f"OPERATION PROFIT, Gross {trade.pnl:.2f}, Net {trade.pnlcomm:.2f}")

    def log(self, txt):
        dt = self.data.datetime.datetime(0)
        print(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}, {txt}")

    def log_order(self, order: bt.order.Order):
        direction = "BUY" if order.isbuy() else "SELL"
        self.log(
            f"{direction} EXECUTED, Size: {order.executed.size}, Price: {order.executed.price:.2f}, Cost: {order.executed.value}, Comm: {order.executed.comm:.2f}"
        )


cerebro = bt.Cerebro()

cerebro.adddata(data)

cerebro.addstrategy(MyStrategy)

cerebro.broker.setcash(1000)
print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

cerebro.addsizer(bt.sizers.FixedSize, stake=10)

cerebro.broker.setcommission(commission=0.0)

cerebro.run()

print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

cerebro.plot()
