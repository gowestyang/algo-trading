# region imports
from AlgorithmImports import *
# endregion

class UpgradedLightBrownMosquito(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        spy = self.AddEquity("SPY", Resolution.Daily)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)

        self.spy = spy.Symbol

        self.SetBenchmark("SPY")
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.entryPrice = 0
        self.period = timedelta(31)
        self.nextEntryTime = self.Time

    def OnData(self, data: Slice):
        if not self.spy in data:
            return

        price = data[self.spy].Close
        # price = data.Bars[self.spy].Close
        # price = self.Securities[self.spy].Close

        if not self.Portfolio.Invested:
            if self.nextEntryTime <= self.Time:
                self.SetHoldings(self.spy, 1.0)
                # self.MarketOrder(self.spy, int(self.Portfolio.Cash / price))
                self.Log("BUY SPY @" + str(price))
                self.entryPrice = price # only for simplicity: the actual filled price can be different
            
        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.9 > price:
            self.Liquidate()
            self.Log("SELL SPY @" + str(price))
            self.nextEntryTime = self.Time + self.period