using System;
using cAlgo.API;
using cAlgo.API.Collections;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;
 
namespace cAlgo
{
    [Levels(100)]
    [Cloud("TrutleTrendTradingSystem", "ZeroLevel", FirstColor = "#00ff00", SecondColor = "#ff0000", Opacity = 0.1)]
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class mTurtleTrendTradingSystem : Indicator
    {
        [Parameter("Entry Period (52)", DefaultValue = 52)]
        public int inpPeriodEntry { get; set; }
        [Parameter("Exit Period (13)", DefaultValue = 13)]
        public int inpPeriodExit { get; set; }
 
        [Output("TrutleTrendTradingSystem", LineColor = "Black", PlotType = PlotType.Line, Thickness = 1)]
        public IndicatorDataSeries outTrutleTrendTradingSystem { get; set; }
        [Output("ZeroLevel", LineColor = "Transparent", PlotType = PlotType.Line, Thickness = 1)]
        public IndicatorDataSeries outZeroLevel { get; set; }
         
        private IndicatorDataSeries _longEntry, _shortEntry, _exitShort, _exitLong, _ttts;
         
 
        protected override void Initialize()
        {
            _longEntry = CreateDataSeries();
            _shortEntry = CreateDataSeries();
            _exitShort = CreateDataSeries();
            _exitLong = CreateDataSeries();
            _ttts = CreateDataSeries();
        }
 
        public override void Calculate(int i)
        {
            _longEntry[i] = i>inpPeriodEntry ? Bars.HighPrices.Maximum(inpPeriodEntry) : Bars.HighPrices[i];
            _shortEntry[i] = i>inpPeriodEntry ? Bars.LowPrices.Minimum(inpPeriodEntry) : Bars.LowPrices[i];
            _exitShort[i] = i>inpPeriodExit ? Bars.HighPrices.Maximum(inpPeriodExit) : Bars.HighPrices[i];
            _exitLong[i] = i>inpPeriodExit ? Bars.LowPrices.Minimum(inpPeriodExit) : Bars.LowPrices[i];
 
            _ttts[i] = i>1 ? _ttts[i-1] : 0;
            if(i>1 && Bars.ClosePrices[i] >= _longEntry[i-1])
                _ttts[i] = +1;
            else
            if(i>1 && Bars.ClosePrices[i] <= _shortEntry[i-1])
                _ttts[i] = -1;
             
            if(i>1 && Bars.LowPrices[i] <= _exitLong[i-1] && _ttts[i] == +1)
                _ttts[i] = 0;
            else
            if(i>1 && Bars.HighPrices[i] >= _exitShort[i-1] && _ttts[i] == -1)
                _ttts[i] = 0;
             
            outTrutleTrendTradingSystem[i] = _ttts[i];
            outZeroLevel[i] = 0;
        }
    }
}