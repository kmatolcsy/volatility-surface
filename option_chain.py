import pandas as pd
from functools import reduce


class OptionChain:
    def __init__(self, ticker, df, verbose=True):
        self.ticker = ticker
        self.df = df

        self.verbose = verbose

        if verbose:
            # cast strike price
            df['Strike'] = df.Strike.astype(float)

            # add mid price
            bid = pd.to_numeric(df.Bid, errors='coerce')
            ask = pd.to_numeric(df.Ask, errors='coerce')

            self.df['Mid'] = 0.5 * (bid + ask)

            # add option expiry date
            maturities = df['Contract Name'].str.replace(ticker, '').str[:6]
            self.df['Maturity'] = pd.to_datetime(maturities, format='%y%m%d')
            self.df['Time to Maturity'] = (self.df.Maturity - pd.Timestamp.today()).dt.days / 365

            # add option type (call/put)
            self.df['Type'] = df['Contract Name'].str.replace(ticker, '').str[6]


    def add_spot(self, value):
        self.df['Spot'] = value

        if self.verbose:
            self.df['Moneyness'] = self.df.Spot / self.df.Strike

        return self


    def add_rate(self, value, name):
        self.df[name] = value

        return self

    
    def get_ticker(self):
        return self.ticker


    def get_df(self):
        return self.df


    def get_price_mx(self, call=True, limits={'Moneyness': [0.75, 1.25]}):
        if not self.verbose: 
            raise Exception('verbose must be set to True')
            # TODO: check required columns too

        limit_conditions = [self.df[k].between(*v) for k, v in limits.items()]

        df = self.df[
            ~ (self.df.Strike % 5).astype(bool)
            & (self.df.Type == 'C' if call else 'P')
            & reduce(lambda x, y: x & y, limit_conditions)
        ]

        return df.pivot(index='Moneyness', columns='Time to Maturity', values='Mid')
