import lzma
import dill as pickle
import pandas as pd
import numpy as np

def load_pickle(path):
    with lzma.open(path,"rb") as fp:
        file = pickle.load(fp)
    return file

def save_pickle(path,obj):
    with lzma.open(path,"wb") as fp:
        pickle.dump(obj,fp)

def get_pnl_stats(date, prev, portfolio_df, insts, idx, dfs):
    day_pnl = 0
    nominal_ret = 0
    for inst in insts:
        units = portfolio_df.loc[idx-1, inst + " units"] # from prev day
        if units != 0:
            delta = dfs[inst].loc[date,"close"] - dfs[inst].loc[prev,"close"]
            inst_pnl = units * delta
            day_pnl += inst_pnl
            nominal_ret += portfolio_df.loc[idx-1, inst + " units"] * dfs[inst].loc[date,"ret"]
    # return on the portfolio (can have more leverage)
    capital_ret = nominal_ret * portfolio_df.loc[idx-1, "leverage"]
    portfolio_df.loc[idx, "capital"] = portfolio_df.loc[idx-1, "capital"] + day_pnl
    portfolio_df.loc[idx, "day_pnl"] = day_pnl
    portfolio_df.loc[idx, "nominal_ret"] = nominal_ret
    portfolio_df.loc[idx, "capital"] = capital_ret
    return day_pnl, capital_ret
    
class Alpha():
    # computes portfolio and PnL details based on stock tickers, list of DataFrames, and start and end dates
    def __init__(self, insts, dfs, start, end) -> None:
        self.insts = insts
        self.dfs = dfs
        self.start = start
        self.end = end

    def init_portfolio_settings(self, trade_range):
        portfolio_df = pd.DataFrame(index=trade_range)\
            .reset_index()\
            .rename(columns={"index":"datetime"})
        portfolio_df.loc[0,"capital"] = 100000
        return portfolio_df

    def compute_meta_info(self, trade_range):
        print(self.insts)
        for inst in self.insts:
            df = pd.DataFrame(index=trade_range)
            # fill missing data: forward fill -> backward fill
            self.dfs[inst] = df.join(self.dfs[inst]).fillna(method="ffill").fillna(method="bfill") 
            # return statistics
            self.dfs[inst]["ret"] = -1 + self.dfs[inst]["close"]/self.dfs[inst]["close"].shift(1) # % return
            sampled = self.dfs[inst]["close"] != self.dfs[inst]["close"].shift(1).fillna(method="bfill") # check if price changed bet 2 days
            # rolling operation
            eligible = sampled.rolling(5).apply(lambda x: int(np.any(x))).fillna(0) # want at least 1 new sample in the last 5 days
            self.dfs[inst]["eligible"] = eligible.astype(int) & (self.dfs[inst]["close"] > 0).astype(int)
            # print(inst)
            # input(self.dfs[inst]) # this stops loop, but not the program (for debugging)
        return None

    def run_simulation(self):
        from datetime import timedelta # debugged bc pytz only not working
        print("running backtest")
        start = self.start + timedelta(hours=5) # eastern time
        end = self.end + timedelta(hours=5) # eastern time
        date_range = pd.date_range(start=start, end=end, freq="D")

        # loop per day
        self.compute_meta_info(trade_range=date_range)
        portfolio_df = self.init_portfolio_settings(trade_range=date_range)
        for i in portfolio_df.index:
            date = portfolio_df.loc[i,"datetime"]
            # define trading universe for the particular day
            eligibles = [inst for inst in self.insts if self.dfs[inst].loc[date,"eligible"]]
            non_eligibles = [inst for inst in self.insts if inst not in eligibles]

            if i != 0:
                # compute PnL
                date_prev = portfolio_df.loc[i-1,"datetime"]
                day_pnl, capital_ret = get_pnl_stats(date=date,
                                                     prev=date_prev,
                                                     portfolio_df=portfolio_df,
                                                     insts=self.insts,
                                                     idx=i,
                                                     dfs=self.dfs)

            # compute alpha scores
            alpha_scores = {}
            import random
            # random signal for now
            for inst in eligibles:
                alpha_scores[inst] = random.uniform(0,1)
            # go long highest alphas, short lowest alphas
            alpha_scores = dict(sorted(alpha_scores.items(), key=lambda x: x[1], reverse=False)) 
            # input(alpha_scores)
            print(alpha_scores)
            alpha_long = list(alpha_scores.keys())[-int(len(alpha_scores)/4):] # top 25%
            alpha_short = list(alpha_scores.keys())[:int(len(alpha_scores)/4)]
            
            # not interesting tickers
            for inst in non_eligibles:
                portfolio_df.loc[i, f"{inst} w"] = 0 # portfolio weight
                portfolio_df.loc[i, f"{inst} units"] = 0 # # of allocs

            nominal_tot = 0 # nominal val of portfolio
            short_ratio = 2/3
            for inst in eligibles:
                # -1, 0, 1 labels
                forecast = 1 if inst in alpha_long else (-1 if inst in alpha_short else 0) # direction of bet
                dollar_allocation = portfolio_df.loc[i,"capital"] / (len(alpha_long) + len(alpha_short)) # divide equally on L/S basket
                #  allocate capital
                if forecast == -1:
                    position = forecast * short_ratio * dollar_allocation / self.dfs[inst].loc[date,"close"]
                else:
                    position = forecast * dollar_allocation / self.dfs[inst].loc[date,"close"]
                portfolio_df.loc[i, inst + " units"] = position
                nominal_tot += abs(position * self.dfs[inst].loc[date,"close"]) # position sizing

            # normalize? what is w and units?
            for inst in eligibles:
                units = portfolio_df.loc[i, inst + " units"]
                nominal_inst = units * self.dfs[inst].loc[date,"close"]
                inst_w = nominal_inst / nominal_tot
                portfolio_df.loc[i, inst + " w"] = inst_w

            portfolio_df.loc[i, "nominal"] = nominal_tot
            portfolio_df.loc[i, "leverage"] = nominal_tot / portfolio_df.loc[i, "capital"]

            if i % 100 == 0:
                # print(f"Long: {alpha_long}, Short: {alpha_short}")
                # input("Next day...")
                # input(portfolio_df.loc[i])
                print(portfolio_df.loc[i])
# alpha = Alpha()
# alpha.run_simulation()