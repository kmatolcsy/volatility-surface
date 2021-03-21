import numpy as np
import pandas as pd
import datetime as dt
from scipy.stats import norm
from scipy.optimize import newton, bisect
from pandas import to_datetime


def aux_variables(spot, strike, rate, vol, ttm):
    d1 = np.log(spot / strike) + (rate + 0.5 * vol ** 2) * ttm
    d2 = d1 - vol * np.sqrt(ttm) 
    return d1, d2


def call_price(spot, strike, rate, vol, ttm):
    d1, d2 = aux_variables(spot, strike, rate, vol, ttm)
    return spot * norm.cdf(d1) - np.exp(-rate * ttm) * strike * norm.cdf(d2)


def put_price(spot, strike, rate, vol, ttm):
    d1, d2 = aux_variables(spot, strike, rate, vol, ttm)
    return np.exp(-rate * ttm) * strike * norm.cdf(-d2) - spot * norm.cdf(-d1)


def vega(spot, strike, rate, vol, ttm):
    d1, _ = aux_variables(spot, strike, rate, vol, ttm)
    return spot * np.sqrt(ttm) * norm.pdf(d1)


def newton_raphson(price, spot, strike, rate, ttm, max_iter=2000, tol=0.000001):
    # only implemented for call
    vol_n = np.sqrt(2 * np.pi / ttm) * price / spot
    price_n = call_price(spot, strike, rate, vol_n, ttm)

    counter = 0

    while np.abs(price_n - price) > tol:
        vol_n -= (price_n - price) / vega(spot, strike, rate, vol_n, ttm)
        price_n = call_price(spot, strike, rate, vol_n, ttm)

        counter += 1

        if counter > max_iter:
            print(f'Convergence failed after {max_iter} iterations. Price diff: {price_n - price}')
            break

    return vol_n


def implied_vol(market_price, spot, strike, rate, ttm, call=True, maxiter=2000):
    if np.isnan(market_price):
        return np.nan

    model_price = call_price if call else put_price # function
    init = np.sqrt(2 * np.pi / ttm) * market_price / spot
    func = lambda x: model_price(spot, strike, rate, x, ttm) - market_price
    fprime = lambda x: vega(spot, strike, rate, x, ttm)

    try: 
        return newton(func, init, fprime, maxiter=maxiter)  
    except RuntimeError:
        return bisect(func, 0.000001, 4, maxiter=maxiter)


def vol_surface(df, spot, rate):
    surface = np.ndarray(df.shape)

    for j, ttm in enumerate(df.columns):
        for i, moneyness in enumerate(df.index):
            market_price = df.loc[moneyness, ttm]
            strike = spot / moneyness 
            
            surface[i, j] = implied_vol(market_price, spot, strike, rate, ttm)

    return pd.DataFrame(index=df.index, columns=df.columns, data=surface)
