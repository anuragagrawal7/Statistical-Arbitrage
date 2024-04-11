import pandas as pd

class ProcessPriceData():
    
    def __init__(self, df):
        self.df = df
    
    def normalize_prices(self):
        dfn = pd.DataFrame()

        for col in self.df.columns:
            dfn[col] = self.df[col]/self.df[col].iloc[0]
            
        return dfn
    
    def datetime_index(self, dt_format = "%d-%m-%Y %H:%M:%S"):
        self.df["DateTime"] = self. df["Date"] + " " + self.df["Time"]
        self.df['DateTime'] = pd.to_datetime(self.df['DateTime'], format=dt_format)
        df = self.df.set_index('DateTime')
        return df
            
    def align_fts_tgt(self, fts, tgt):
        fts1 = fts.dropna()
        tgt1 = tgt.dropna()
        ft_idx = fts1.index[0]
        tgt_idx = tgt1.index[0]
        idx = max(ft_idx, tgt_idx)
        fts = fts[idx:]
        tgt = tgt[idx:]
        
        return fts, tgt
        
        