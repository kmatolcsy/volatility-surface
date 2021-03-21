import datetime as dt
from pandas import to_datetime


class Date:
    def __init__(self, yahoo_date):
        self._yahoo_date = int(yahoo_date)
        self._excel_date = self._yahoo_date / 86400 + 25569
        self._snake_date = to_datetime(self._excel_date, unit='D', origin='1899-12-30')


    def get_yahoo_date(self):
        return self._yahoo_date


    def get_excel_date(self):
        return self._excel_date


    def get_snake_date(self):
        return self._snake_date


    def is_third_friday(self):
        return self._snake_date.weekday() == 4 and 15 <= self._snake_date.day <= 21


    def is_later_than(self, date=None, days=0):
        if not date:
            date = dt.datetime.today()

        return self._snake_date > date + dt.timedelta(days=days)
