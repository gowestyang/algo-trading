# region imports
from AlgorithmImports import *
# endregion

# this is to demonstrate how to create a customized SMA indicator
from collections import deque

class CustomSimpleMovingAverage(PythonIndicator):
    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen=period)
    
    def Update(self, input):
        self.queue.appendleft(input.Close)
        self.Time = input.EndTime
        count = len(self.queue)
        self.Value = sum(self.queue) / count
        # note here you don't need to build "IsReady"
        return (count == self.queue.maxlen)

class EnergeticGreenGaur(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        #self.sma = self.SMA(self.spy, 30, Resolution.Daily)
        ## here we load history data so there is not need to wait
        ## as a result, in OnData() we actually don't nere to check IsReady, but we just leave it there as an example.
        #closing_prices = self.History(self.spy, 30, Resolution.Daily)["close"]
        #for time, price in closing_prices.loc[self.spy].items():
        #    self.sma.Update(time, price)

        self.sma = CustomSimpleMovingAverage("CustomSMA", 30)
        self.RegisterIndicator(self.spy, self.sma, Resolution.Daily)

    def OnData(self, data: Slice):
        if not self.sma.IsReady:
            return
        
        # by right, we should use rolling window which is more efficient
        # alternatively, you can use min/max indicator directly
        # here we just want to demonstrate historical data as an example
        # if you use number of bars to query one year, it should be 252 days
        hist = self.History(self.spy, timedelta(365), Resolution.Daily)
        low = min(hist["low"])
        high = max(hist["high"])

        price = self.Securities[self.spy].Price

        if price * 1.05 >= high and self.sma.Current.Value < price:
            if not self.Portfolio[self.spy].IsLong:
                self.SetHoldings(self.spy, 1)
        elif price * 0.95 <= low and self.sma.Current.Value > price:
            if not self.Portfolio[self.spy].IsShort:
                self.SetHoldings(self.spy, -1)
        else:
            self.Liquidate()
        
        self.Plot("Benchmark", "52w-High", high)
        self.Plot("Benchmark", "52w-low", low)
        self.Plot("Benchmark", "SMA", self.sma.Current.Value)


