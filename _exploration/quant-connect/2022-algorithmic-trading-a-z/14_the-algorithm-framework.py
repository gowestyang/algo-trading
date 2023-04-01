# region imports
from AlgorithmImports import *
# endregion

from AlphaModel import *

class EnergeticGreenGaur(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)
        
        self.month = 0
        self.num_coarse = 500 # number of stocks considered in the universe

        self.UniverseSettings.Resolution = Resolution.Daily
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)

        self.AddAlpha(FundamentalFactorAlphaModel())

        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel(self.IsRebalanceDue))

        self.SetRiskManagement(NullRiskManagementModel())

    
    def IsRebalanceDue(self, time):
        if time.month == self.month or time.month not in [1,4,7,10]:
            return None
        
        self.month = time.month
        return time

    def CoarseSelectionFunction(self, coarse):
        if not self.IsRebalanceDue(self.Time):
            return Universe.Unchanged
        
        selected = sorted([x for x in coarse if x.HasFundamentalData and x.Price>5], key=lambda x: x.DollarVolume, reverse=True)

        return [x.Symbol for x in selected[:self.num_coarse]]

    def FineSelectionFunction(self, fine):
        sectors = [
            MorningstarSectorCode.FinancialServices,
            MorningstarSectorCode.RealEstate,
            MorningstarSectorCode.Healthcare,
            MorningstarSectorCode.Utilities,
            MorningstarSectorCode.Technology
        ]

        filtered_fine = [x.Symbol for x in fine 
                if x.SecurityReference.IPODate + timedelta(5*365) < self.Time 
                and x.AssetClassification.MorningstarSectorCode in sectors
                and x.OperationRatios.ROE.Value > 0
                and x.OperationRatios.NetMargin.Value > 0
                and x.ValuationRatios.PERatio > 0]

        return filtered_fine
        