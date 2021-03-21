import requests
import bs4 as bs
import pandas as pd

from date import Date


class YahooFinance:
    def __init__(self, ticker, skip_days=14):
        self.ticker = ticker
        self.skip_days = skip_days
        self.url = f'http://finance.yahoo.com/quote/{ticker}/options'


    def get_spot(self):
        src = requests.get(self.url)

        soup = bs.BeautifulSoup(src.content, 'lxml')
        span = soup.find('span', {'data-reactid': '32'})

        return float(span.text)


    def get_maturities(self):
        # monthly maturities only
        src = requests.get(self.url)

        soup = bs.BeautifulSoup(src.content, 'lxml')
        options = soup.find('select').find_all('option')

        dates = [Date(option.get('value')) for option in options]

        return [date for date in dates if date.is_third_friday() \
            and date.is_later_than(days=self.skip_days)]


    def get_options(self, date):
        params = f'?date={date.get_yahoo_date()}'

        src = requests.get(self.url + params)
        dfs = pd.read_html(src.text)

        # assert len(dfs) == 2

        return pd.concat(dfs)


    def get_chain(self):
        maturities = self.get_maturities()
        dfs = [self.get_options(m) for m in maturities]

        return pd.concat(dfs)


if __name__ == '__main__':
    pass
