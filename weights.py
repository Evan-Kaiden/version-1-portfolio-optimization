import pandas as pd
import yfinance as yf
from pypfopt import EfficientFrontier
from pypfopt import CovarianceShrinkage
from pypfopt import expected_returns, objective_functions

from financials import get_tickers

import scipy.sparse.linalg as sparla
import warnings

warnings.filterwarnings("ignore", message="The default fill_method='pad' in DataFrame.pct_change is deprecated", category=FutureWarning)
warnings.filterwarnings("ignore", message ="max_sharpe transforms the optimization problem so additional objectives may not work as expected", category=UserWarning)

def opt(tickers, start_date, end_date):
    stock_data = get_data(tickers, start_date=start_date, end_date=end_date)
    mu = expected_returns.mean_historical_return(stock_data)
    S = CovarianceShrinkage(stock_data).ledoit_wolf()
    try: 
        ef = EfficientFrontier(mu, S, weight_bounds=(0, 1), solver='ECOS')
        ef.add_objective(objective_functions.L2_reg, gamma=0.5)
        weights = ef.max_sharpe()
        weights = ef.clean_weights(cutoff = 0.01)
        weights_series = pd.Series(weights)
        weights_series = weights_series[weights_series != 0]
        return weights_series
    except sparla.ArpackNoConvergence:
        ef = EfficientFrontier(mu, S, weight_bounds=(0, 1))
        weights = ef.max_sharpe()
        weights = ef.clean_weights(cutoff = 0.01)
        weights_series = pd.Series(weights)
        weights_series = weights_series[weights_series != 0]
        return weights_series

def get_data(tickers, start_date, end_date):
    data = yf.download(tickers=tickers, start=start_date, end=end_date, progress=False)['Adj Close']
    return data


def get_series(tickers, start_date, end_date):
    weights_series = opt(tickers, start_date=start_date, end_date=end_date)
    return weights_series

def get_weights(start_date, end_date):
    tickers = get_tickers()
    return get_series(tickers, start_date, end_date)
