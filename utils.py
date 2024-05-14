import lzma
import dill as pickle

def load_pickle(path):
    with lzma.open(path,"rb") as fp:
        file = pickle.load(fp)
    return file

def save_pickle(path,obj):
    with lzma.open(path,"wb") as fp:
        pickle.dump(obj,fp)

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
            .rename(columns={"index":"datetime"})
        portfolio_df.loc[0,"capital"] = 10000
        return portfolio_df
    
    def compute_meta_info(self, trade_range):
        print(self.insts)
        for inst in self.insts:
            df = pd.DataFrame(index=trade_range)
            self.dfs[inst] = df.join(self.dfs[inst]).fillna(method="ffill").fillna(method="bfill")
            print(df.shape)
            print(self.dfs[inst])
            input("See") # this stops loop, but not the program (for debugging)

    def run_simulation(self):
        from datetime import timedelta # debugged bc pytz only not working
        print("running backtest")
        start = self.start + timedelta(hours=5) # eastern time
        end = self.end + timedelta(hours=5) # eastern time
        date_range = pd.date_range(start=start, end=end, freq="D")

        self.compute_meta_info(trade_range=date_range)
        portfolio_df = self.init_portfolio_settings(trade_range=date_range)
        for i in portfolio_df.index:
            date = portfolio_df.loc[i,"datetime"]

            if i != 0:
                # compute PnL
                pass
            alpha_scores = {}
            # compute alpha signals

            # compute positions & other info


# alpha = Alpha()
# alpha.run_simulation()