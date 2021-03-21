import numpy as np
import pandas as pd
import quandl as qd
from scipy.interpolate import griddata
from plotly.offline import plot

from yahoo_finance import YahooFinance
from option_chain import OptionChain
from black_scholes import vol_surface
from models import DumasFlemingWhaley
from utils import make_dir, update_repo, send_notification


def interpolate(df, method='linear'):
    x, y = np.meshgrid(df.columns, df.index)
    z = np.ma.masked_invalid(df.values)

    xm = x[~z.mask]
    ym = y[~z.mask]
    zm = z[~z.mask]

    data = griddata((xm, ym), zm.ravel(), (x, y), method=method)

    return pd.DataFrame(index=df.index, columns=df.columns, data=data)


def plot_surface(df):
    return plot({
        'data': [{
            'x': df.columns,
            'y': df.index,
            'z': df.values,
            'type': 'surface'
        }]
    })


@send_notification
def main():
    ticker = 'SPY'

    root = './data'
    path = make_dir(root)

    # scraping 
    yf = YahooFinance(ticker)

    chain = yf.get_chain()
    spot = yf.get_spot()

    array = qd.get('FRED/FEDFUNDS', rows=1, returns='numpy')
    rate = array[0][1]
    
    # option chain
    oc = OptionChain(ticker, chain).add_spot(spot).add_rate(rate, name='Fed Funds Rate (%)')
    oc.get_df().to_csv(f'{path}/option_chain.csv')

    # call prices
    call_prices = oc.get_price_mx()
    call_prices.to_csv(f'{path}/call_prices.csv')

    # implied vols
    implied_vols = vol_surface(call_prices, spot, rate/100)
    implied_vols.to_csv(f'{path}/implied_vols.csv')

    # interpolated surfaces
    interp_linear = interpolate(implied_vols, 'linear')
    interp_linear.to_csv(f'{path}/implied_vols_interpolated_lin.csv')

    interp_cubic = interpolate(implied_vols, 'cubic')
    interp_cubic.to_csv(f'{path}/implied_vols_interpolated_cub.csv')

    # parametric models
    model = DumasFlemingWhaley()

    model.fit(implied_vols.reset_index())
    model.get_surface().to_csv(f'{path}/implied_vols_parametric_dfw.csv')

    # update repo
    update_repo(root)

    return


if __name__ == '__main__':
    main()
