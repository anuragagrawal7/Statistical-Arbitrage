import pandas as pd

class ProcessPriceData():
    
    def __init__(self, df):
        self.df = df
    
    def normalize_prices(self):
        dfn = pd.DataFrame()

        for col in self.df.columns:
            dfn[col] = self.df[col]/self.df[col].iloc[0]
        
        return dfn