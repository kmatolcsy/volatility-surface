import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline


class DumasFlemingWhaley:
    def __init__(self, order=2):
        self.pipe = Pipeline([
            ('trf', PolynomialFeatures(order)), 
            ('rgr', LinearRegression())
        ])

    def fit(self, pivot):
        df = pivot.melt('Moneyness', var_name='TTM', value_name='IV')
        df = df.dropna()

        x = df[['Moneyness', 'TTM']].values.astype(float) 
        y = df.IV.values.astype(float)

        self.pipe.fit(x, y)

    @staticmethod
    def create_cartesian(a, b):
        return np.array([np.repeat(a, b.shape[0]), np.tile(b, a.shape[0])]).T

    def get_surface(self):
        moneyness = np.linspace(0.75, 1.25, num=11)
        ttm = np.linspace(0, 2, num=9)

        x = self.create_cartesian(moneyness, ttm)
        y = self.pipe.predict(x).reshape((11, 9))

        return pd.DataFrame(y, moneyness, ttm).rename_axis(index='Moneyness')


if __name__ == '__main__':
    pivot = pd.read_csv('./data/2021-03-20/implied_vols.csv')

    model = DumasFlemingWhaley()
    model.fit(pivot)

    ans = model.get_surface()
    print(ans)
