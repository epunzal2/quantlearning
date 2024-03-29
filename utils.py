import lzma
import dill as pickle

def load_pickle(path):
    try:
        with lzma.open(path, 'rb') as fp:
            file = pickle.load(fp)
        return file
    except:
        return None

def save_pickle(path, obj):
    with lzma.open(path, 'wb') as fp:
        pickle.dump(obj, fp)

import pandas as pd
class Alpha():

    def __init__(self, insts, dfs, start, end) -> None:
        self.insts = insts
        self.dfs = dfs
        self.start = start
        self.end = end

    def init_portfolio_settings(self, trade_range):
        portfolio_df = pd.DataFrame(index=trade_range)\
            .reset_index()\
            .rename(columns={"index": "datetime"})
        portfolio_df.loc[0,"capital"] = 10000
        return portfolio_df
    
    def compute_meta_info(self, trade_range):
        pass

    def run_simulation(self):
        print("Running backtest...")
        date_range = pd.date_range(start=self.start, end=self.end, freq="D")
        print(date_range)