import pandas as pd
from pandas_datareader import data
import datetime
import numpy as np
import warnings
from django.http import Http404


# FUNCTIONS:
def build_stock_dataset(currency, start_date, stock_tickers, price_point):
    '''
    Builds a DataFrame for a number of stocks consisting of
    both date and price.

    stock_tickers (list): list of crypto ticker symbols.
    currency (string): the currency to be used.
    price_point (string): the type of price point to use eg. 'Adj Close', 'Open'...
    start_date (datetime): when to start gathering data.

    Returns: a DataFrame of stock prices.
    '''
    end_date = datetime.datetime.now()

    # Read in the data.
    currency_conversion = f'USD{currency}=X'
    forex_data = data.DataReader(currency_conversion, 'yahoo', start_date, end_date)
    current_rate = forex_data.iloc[-1, 5]
    stock_data = data.DataReader(stock_tickers, 'yahoo', start_date, end_date)

    stock_data = stock_data[price_point]
    stock_data = stock_data * current_rate

    # Remove index and column headings.
    stock_data = stock_data.rename_axis(None, axis=0)
    stock_data = stock_data.rename_axis(None, axis=1)

    # Turn index from datetime to date.
    stock_data.index = stock_data.index.date

    return stock_data


# CLASSES:

class Prices:
    def __init__(self, currency, start_date, stock_tickers, price_point):
        """
        Initializes a Prices object
        """
        self.portfolio = build_stock_dataset(currency, start_date, stock_tickers, price_point)
        # Generate price data:
        self.prices = self.portfolio.copy()
        # Round figures.
        for column in range(len(self.portfolio.columns)):
            if self.portfolio.iloc[-1, column] < 1:
                self.prices.iloc[:, column] = self.prices.iloc[:, column].round(5)
            else:
                self.prices.iloc[:, column] = self.prices.iloc[:, column].round(2)
        # Get the value of the overall portfolio.
        self.prices['Portfolio'] = self.prices.sum(1).round(2)

    def get_names_prices_returns(self):
        price_data = self.prices.copy()
        headings = price_data.columns.tolist()[::-1]
        prices = np.array([float(price) for price in price_data.iloc[-1].values])[::-1]
        print(prices)
        if len(price_data.index) > 1:
            penultimate_prices = np.array([float(price) for price in price_data.iloc[-2].values])[::-1]
        else:
            penultimate_prices = prices.copy()
        daily_returns = np.round(((prices - penultimate_prices)/penultimate_prices)*100,2)
        return zip(headings, prices, daily_returns)

    def order_by_total_return(self):
        price_data = self.prices.copy()
        headings = price_data.columns.tolist()
        prices = np.array([float(price) for price in price_data.iloc[-1].values])
        initial_prices = price_data.iloc[0].values.tolist()
        initial_prices = np.array(initial_prices)
        total_returns = np.round(((prices - initial_prices)/initial_prices)*100,2)
        return_dict = dict(zip(headings, total_returns))
        sorted_return_dict = {k: v for k, v in sorted(return_dict.items(), key=lambda item: item[1], reverse=True)}
        sorted_headings = list(sorted_return_dict.keys())
        sorted_returns = list(sorted_return_dict.values())
        return sorted_headings, sorted_returns

    def get_benchmarked_returns(self, index_ticker, currency, start_date, price_point):
        prices = self.prices.copy()
        end_date = datetime.datetime.now()
        benchmark = data.DataReader(index_ticker, 'yahoo', start_date, end_date)[price_point]
        currency_conversion = f'USD{currency}=X'
        forex_data = data.DataReader(currency_conversion, 'yahoo', start_date, end_date)
        current_rate = forex_data.iloc[-1, 5]
        benchmark *= current_rate
        print(prices)
        print(benchmark)
        benchmarked_prices = pd.concat([prices, benchmark], axis=1)
        benchmarked_prices.dropna(inplace=True)
        benchmarked_returns = benchmarked_prices.pct_change(1)
        benchmarked_returns = benchmarked_returns.replace([np.inf, -np.inf], np.nan).dropna()
        benchmarked_returns *= 100
        benchmarked_returns = benchmarked_returns.round(2)
        benchmarked_returns.rename({'Adj Close': index_ticker}, axis=1, inplace=True)
        return benchmarked_returns

    def get_prices(self):
        return self.prices

# HEALTH PORTFOLIO
def calc_longevity(weekly_activity):
    additional_years = 0
    # 0-0.5 hours
    if weekly_activity <= datetime.timedelta(hours=0.25):
        return additional_years
    # 0.5-1 hours
    elif weekly_activity <= datetime.timedelta(hours=0.5):
        additional_years = 1
        return additional_years
    # 1-1.5 hours
    elif weekly_activity <= datetime.timedelta(hours=1):
        additional_years = 2
        return additional_years
    # 1.5-2 hours
    elif weekly_activity <= datetime.timedelta(hours=1.5):
        additional_years = 3
        return additional_years
    # 2-2.75 hours
    elif weekly_activity <= datetime.timedelta(hours=2):
        additional_years = 4
        return additional_years
    # 2.75-3.75 hours
    elif weekly_activity <= datetime.timedelta(hours=2.75):
        additional_years = 5
        return additional_years
    # 3.75-4.75 hours
    elif weekly_activity <= datetime.timedelta(hours=3.5):
        additional_years = 6
        return additional_years
    # 4.75-6 hours
    elif weekly_activity <= datetime.timedelta(hours=4.5):
        additional_years = 7
        return additional_years
    # 6-7.5 hours
    elif weekly_activity <= datetime.timedelta(hours=5.75):
        additional_years = 8
        return additional_years
    # 7.5-9 hours
    elif weekly_activity <= datetime.timedelta(hours=7):
        additional_years = 9
        return additional_years
    # 9+ hours
    else:
        additional_years = 10
        return additional_years

def calc_mobility(activity_dict):
    weight_dict = {
        'WALK': 1,
        'GYM': 2,
        'OTHER': 2,
        'CYCLE': 3,
        'RUN': 3
    }

    total_mobility = datetime.timedelta()
    for activity in activity_dict.keys():
        activity_weight = weight_dict[activity]
        activity_hours = activity_dict[activity]
        total_mobility = total_mobility + (activity_weight * activity_hours)

    mobility_index = 1
    # 0-4 hours
    if total_mobility <= datetime.timedelta(hours=0.25):
        return mobility_index
    # 4-6 hours
    elif total_mobility <= datetime.timedelta(hours=0.5):
        mobility_index = 2
        return mobility_index
    # 6-8 hours
    elif total_mobility <= datetime.timedelta(hours=1):
        mobility_index = 3
        return mobility_index
    # 8-10 hours
    elif total_mobility <= datetime.timedelta(hours=2):
        mobility_index = 4
        return mobility_index
    # 10-12 hours
    elif total_mobility <= datetime.timedelta(hours=3.25):
        mobility_index = 5
        return mobility_index
    # 12-14 hours
    elif total_mobility <= datetime.timedelta(hours=4.75):
        mobility_index = 6
        return mobility_index
    # 14-16 hours
    elif total_mobility <= datetime.timedelta(hours=6.5):
        mobility_index = 7
        return mobility_index
    # 16-18 hours
    elif total_mobility <= datetime.timedelta(hours=8.5):
        mobility_index = 8
        return mobility_index
    # 18-20 hours
    elif total_mobility <= datetime.timedelta(hours=10.75):
        mobility_index = 9
        return mobility_index
    # 20-22 hours
    elif total_mobility <= datetime.timedelta(hours=13.25):
        mobility_index = 10
        return mobility_index
    # 22-24 hours
    elif total_mobility <= datetime.timedelta(hours=16):
        mobility_index = 11
        return mobility_index
    # 24+ hours
    else:
        mobility_index = 12
        return mobility_index

def calc_wellness(longevity_expected, longevity_earned, mobility):
    additional_longevity = longevity_earned - longevity_expected
    wellness_score = additional_longevity + mobility
    wellness_percentage = int((wellness_score / 24)*100)
    return wellness_percentage

# ENVIRONMENTAL PORTFOLIO
def emissions_saved(activity_dict):
    emissions_dict = {}
    for activity, value in activity_dict.items():
        if activity == 'BUS':
            emissions_dict[activity] = round((value/100)*4.5*2.68,2)
        elif activity == 'TRAIN':
            emissions_dict[activity] = round((value/100)*2.65*2.68,2)
        elif activity == 'CAR':
            emissions_dict[activity] = round((value/100)*5.5*2.68,2)
        elif activity == 'PLANE':
            emissions_dict[activity] = round((value/100)*6*2.68,2)
        elif activity == 'OTHER':
            emissions_dict[activity] = round((value/100)*2.68,2)
        else:
            continue

    return emissions_dict


# WEALTH PORTFOLIO