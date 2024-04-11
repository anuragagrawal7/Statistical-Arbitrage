import pandas as pd
import talib as ta
import warnings
from statsmodels.api import OLS

warnings.filterwarnings("ignore")

class StatisticalArbitrage():
    
    def __init__(self, inst1_n, inst2_n):
        self.inst1_n = inst1_n
        self.inst2_n = inst2_n
        
    
    def calculate_hedge_ratio(self, i, look_back, model):
        
        if i < look_back-1:
            pass
        
        if (i+1) % look_back == 0:
            model = OLS(self.inst1_n.iloc[i-look_back+1:i], self.inst2_n.iloc[i-look_back+1:i])
            model = model.fit()

        val = self.inst1_n.iloc[i] - model.params[0] * self.inst2_n.iloc[i]

        return val, model
    
    def spread_margin(self, hedge_ratio, leverage1=1, leverage2=1):
    
        return (self.inst1_n.iloc[-1]/leverage1) + (hedge_ratio*self.inst2_n.iloc[-1]/leverage2)
    
    def bollinger_bands_on_spread(self, sprd, timeperiod, nbdevup, nbdevdn, long_target, short_target):
        bb = pd.DataFrame()
        bb['Spread'] = sprd['Spread'].iloc[-1-timeperiod:]
        bb['Margin'] = sprd['Margin'].iloc[-1-timeperiod:]
        bb['upper_band'], bb['middle_band'], bb['lower_band'] = ta.BBANDS(bb['Spread'], timeperiod =timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
        bb['STDEV'] = bb['Spread'].rolling(window=timeperiod).std()
        bb['long_target_band'] = bb['middle_band'] + long_target*bb['STDEV']
        bb['short_target_band'] = bb['middle_band'] - short_target*bb['STDEV']
        bb.dropna(inplace=True)
        return bb
    
    def bollinger_signals(self, bb):
        
        signal = 'No Signal'
        
        # Long
        if bb['Spread'].iloc[-1] <= bb['lower_band'].iloc[-1]:
            signal = 'Long'

        # Short
        elif bb['Spread'].iloc[-1] >= bb['upper_band'].iloc[-1]:
            signal = 'Short'

        # Short Square Off
        elif bb['Spread'].iloc[-1] <= bb['short_target_band'].iloc[-1] and bb['Spread'].iloc[-1] > bb['lower_band'].iloc[-1]:
            signal = 'Short Square Off'

        # Long Square Off
        elif bb['Spread'].iloc[-1] >= bb['long_target_band'].iloc[-1] and bb['Spread'].iloc[-1] < bb['upper_band'].iloc[-1]:
            signal = 'Long Square Off'
            
        return signal