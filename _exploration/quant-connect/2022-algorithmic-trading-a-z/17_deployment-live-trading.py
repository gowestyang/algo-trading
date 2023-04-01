# region imports
from AlgorithmImports import *
# endregion

class EnergeticGreenGaur(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000) # this is only for back-testing; in live trading, your account balance will be used.
        self.symbol = self.AddEquity("QQQ", Resolution.Hour).Symbol
        self.bnd = self.AddEquity("BND", Resolution.Hour).Symbol

        length = 30
        self.sma = self.SMA(self.symbol, length, Resolution.Daily)

        # History warm up for shortcut helper SMA indicator
        closing_prices = self.History(self.symbol, length, Resolution.Daily)["close"]
        for time, price in closing_prices.loc[self.symbol].items():
            self.sma.Update(time, price)

        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.SetBenchmark(self.symbol)
        self.rebalanceTime = datetime.min
        self.uptrend = True

        self.Schedule.On(
            self.DateRules.EveryDay(self.symbol),
            self.TimeRules.BeforeMarketClose(self.symbol, 10),
            self.indicatorPlot
            )

    def OnData(self, data):
        if not self.sma.IsReady or self.symbol not in data or self.bnd not in data:
            return
        if self.symbol in data.Dividends and self.symbol not in data.Bars:
            self.Debug("Dividend paid at time "+str(self.Time))
            return
        
        trend = data[self.symbol].Price >= self.sma.Current.Value

        if self.Time >= self.rebalanceTime or trend != self.uptrend:
            self.trade(trend)
        
    def trade(self, trend):
        if trend:
            # uptrend
            self.SetHoldings(self.symbol, 0.8)
            self.SetHoldings(self.bnd, 0.2)
            self.uptrend = True
        else:
            # downtrend
            self.SetHoldings(self.symbol, 0.2)
            self.SetHoldings(self.bnd, 0.8)
            self.uptrend = False
        self.rebalanceTime = self.Time + timedelta(30)

    def indicatorPlot(self):
        self.Plot("Benchmark", "SMA_" + str(self.symbol), self.sma.Current.Value)
        # The LiveMode flag can tell whether this algo is in backtest / live-trading.
        if self.LiveMode:
            self.Log("Price: " + str(self.Securities[self.symbol].Price) + ", SMA: " + str(self.sma.Current.Value))

