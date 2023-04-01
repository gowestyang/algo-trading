import json
from src.utils import logging, logger, send_log
import backtrader as bt
import btoandav20 as bto

# App configuration
APP_CONFIG_FILE = 'src/config/app.json'
with open(APP_CONFIG_FILE) as f:
    d_app_config = json.load(f)

DEBUG_MODE = d_app_config['debug']

# Config logger
if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Oanda configuration
ACCOUNT_CONFIG_FILE = 'src/config/oanda.json'
with open(ACCOUNT_CONFIG_FILE) as f:
    d_accounts = json.load(f)

oanda_token = d_accounts['oanda_token']
oanda_account_id = d_accounts['oanda_account_id']

OANDA_IS_LIVE = False

# Instrument, store and data
INSTRUMENT = 'EUR_USD'

config_oanda_store = dict(
    token=oanda_token,
    account=oanda_account_id,
    practice=not OANDA_IS_LIVE,
    notif_transactions=True,
    stream_timeout=10,
)
oanda_store = bto.stores.OandaV20Store(**config_oanda_store)

config_oanda_data = dict(
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
    tz='America/New_York',
    backfill=False,
    backfill_start=False,
)
oanda_data = oanda_store.getdata(dataname=INSTRUMENT, **config_oanda_data)
oanda_data.resample(
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
)

# Define trading strategy
ORDER_SIZE = 10
SL_DISTANCE = 0.00025
TP_DISTANCE = 0.00025

class TestStrategy(bt.Strategy):

    def __init__(self):
        # Display data parameters
        data_params = self.datas[0].params
        send_log(f"INITIALIZE STRATEGY: instrument = {data_params.dataname}, timezone = {data_params.tz}, timeframe = {data_params.timeframe}")

        self.dataclose = self.datas[0].close

        self.order = None
        
    def next(self):
        self._log(f"close = {self.dataclose[0]:.5f}, previous close = {self.dataclose[-1]:.5f}", level=logging.DEBUG)

        # Avoid duplicated order if there is already a pending order
        if self.order:
            return

        if not self.position:
            current_close = self.dataclose[0]
            if current_close > self.dataclose[-1]:
                sl_price = current_close - SL_DISTANCE
                tp_price = current_close + TP_DISTANCE
                self._log(f"CREATE ORDER - MARKET BUY: sl = {sl_price:.5f}, tp = {tp_price:.5f}")
                self.order = self.buy_bracket(
                    size=ORDER_SIZE,
                    exectype=bt.Order.Market,
                    stopprice=sl_price,
                    stopexec=bt.Order.Stop,
                    limitprice=tp_price,
                    limitexec=bt.Order.Limit,
                )
            if current_close < self.dataclose[-1]:
                sl_price = current_close + SL_DISTANCE
                tp_price = current_close - TP_DISTANCE
                self._log(f"CREATE ORDER - MARKET SELL: sl = {sl_price:.5f}, tp = {tp_price:.5f}")
                self.order = self.sell_bracket(
                    size=ORDER_SIZE,
                    
                    exectype=bt.Order.Market,
                    stopprice=sl_price,
                    stopexec=bt.Order.Stop,
                    limitprice=tp_price,
                    limitexec=bt.Order.Limit,
                )

    def notify_order(self, order: bt.order.Order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            self._log_order(order)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self._log(f"ORDER CANCELED / MARGIN / REJECTED: {order.status}")
        
        else:
            self._log(f"WARNING: unknown order status: {order.status}", level=logging.WARNING)

        # Write down - no pending order
        self.order = None

    def notify_trade(self, trade: bt.trade.Trade):
        if not trade.isclosed:
            return
        self._log_trade(trade)

    def _log(self, txt, level=logging.INFO):
        dt = self.datas[0].datetime.datetime(0).strftime("%Y-%m-%d %H:%M:%S")
        send_log(f"({dt}) {txt}", level=level)
    
    def _log_order(self, order: bt.order.Order):
        direction = 'BUY' if order.isbuy() else 'SELL'
        s_comm = f", comm = {order.executed.comm:.5f}" if order.executed.comm > 0 else ""
        self._log(f"ORDER EXECUTED - {direction}: size = {order.executed.size}, price = {order.executed.price:.5f}, cost = {order.executed.value:5f}{s_comm}")

    def _log_trade(self, trade: bt.trade.Trade):
        self._log(f"TRADE COMPLETED: value = {trade.value:.5f}, gross profit = {trade.pnl:.5f}, net profit = {trade.pnlcomm:.5f}")


# Initialize backtrader
cerebro = bt.Cerebro()

cerebro.adddata(oanda_data)
cerebro.setbroker(oanda_store.getbroker())
cerebro.addstrategy(TestStrategy)

cerebro.run()
