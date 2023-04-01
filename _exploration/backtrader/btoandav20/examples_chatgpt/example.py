import time
import backtrader as bt
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts
from oandapyV20.contrib.requests import MarketOrderRequest

# Oanda API configuration
api_key = 'YOUR_API_KEY'
account_id = 'YOUR_ACCOUNT_ID'
api = API(access_token=api_key)
instrument = 'EUR_USD'

class SimpleMovingAverageStrategy(bt.Strategy):
    params = (('sma_short', 50), ('sma_long', 200))

    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_short)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_long)

    def next(self):
        if self.position.size == 0:
            if self.sma_short[0] > self.sma_long[0]:
                self.buy()
        elif self.sma_short[0] < self.sma_long[0]:
            self.sell()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                print('Buy order executed at', order.executed.price)
                place_order(order.executed.price, 'buy')
            elif order.issell():
                print('Sell order executed at', order.executed.price)
                place_order(order.executed.price, 'sell')

# Function to execute orders in Oanda
def place_order(price, order_type):
    if order_type == 'buy':
        units = 1000
    elif order_type == 'sell':
        units = -1000

    market_order = MarketOrderRequest(instrument=instrument, units=units)
    order_endpoint = orders.OrderCreate(accountID=account_id, data=market_order.data)
    api.request(order_endpoint)
    print(f"{order_type.capitalize()} order placed for {instrument} at {price}")

# Initialize backtrader
cerebro = bt.Cerebro()
cerebro.addstrategy(SimpleMovingAverageStrategy)

# Data feed
data = bt.feeds.OandaV20Live(
    account=account_id,
    token=api_key,
    instrument=instrument,
    timeframe=bt.TimeFrame.Days,
    compression=1,
    qcheck=1.0,
    historical=False
)

cerebro.adddata(data)
cerebro.broker.setcash(100000.0)
cerebro.broker.setcommission(commission=0.0001)

# Run the strategy
cerebro.run()