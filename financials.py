import pandas as pd
import yfinance as yf

def sp500():
    return list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0].Symbol)


def get_rating(ticker):
    profitability_score = 0
    leverage_score = 0
    operating_efficiency_score = 0
    valuation_score = 0

    ticker_obj = yf.Ticker(ticker)
    balance_sheet = ticker_obj.quarterly_balance_sheet.T
    income_statement = ticker_obj.quarterly_financials.T
    cfs = ticker_obj.quarterly_cashflow.T
    years = balance_sheet.index
    try:
    # Profitablilty
        # Scores 1 and 2 - net income
        net_income = income_statement['Net Income'][years[0]]
        net_income_py = income_statement['Net Income'][years[1]]
        ni_score = 1 if net_income > 0 else 0
        ni_score_2 = 1 if net_income > net_income_py else 0

        # Score 3 - operating cash flow
        op_cf = cfs['Operating Cash Flow'][years[0]]
        op_cf_score = 1 if op_cf > 0 else 0

        # Score 4 - return on assests
        avg_assets = (balance_sheet['Total Assets'][years[0]] + balance_sheet['Total Assets'][years[1]]) / 2
        avg_assets_py = (balance_sheet['Total Assets'][years[1]] + balance_sheet['Total Assets'][years[2]]) / 2
        RoA = net_income / avg_assets
        RoA_py = net_income_py / avg_assets_py
        RoA_score = 1 if RoA > RoA_py else 0

        # Score 5 - accurals
        total_assets = balance_sheet['Total Assets'][years[0]]
        accruals = op_cf / total_assets - RoA
        ac_score = 1 if accruals > 0 else 0

        profitability_score = ni_score + ni_score_2 + op_cf_score + RoA_score + ac_score

    # Leverage
        # Score 6 - long term debt ratio
        try:
            lt_debt = balance_sheet['Long Term Debt'][years[0]]
            total_assets = balance_sheet['Total Assets'][years[0]]
            debt_ratio = lt_debt / total_assets
            debt_ratio_score = 1 if debt_ratio < 0.4 else 0
        except:
            debt_ratio_score = 1

        # Score 7 - current assests to liablity ratio
        current_assets = balance_sheet['Current Assets'][years[0]]
        current_liab = balance_sheet['Current Liabilities'][years[0]]
        current_ratio = current_assets / current_liab
        current_ratio_score = 1 if current_ratio > 1 else 0

        leverage_score = debt_ratio_score + current_ratio_score

    # Operating Effeciency
        # Score 8 - gross margin
        gp = income_statement['Gross Profit'][years[0]]
        gp_py = income_statement['Gross Profit'][years[1]]
        revenue = income_statement['Total Revenue'][years[0]]
        revenue_py = income_statement['Total Revenue'][years[1]]
        gm = gp / revenue
        gm_py = gp_py / revenue_py
        gm_score = 1 if gm > gm_py else 0

        # Score 9 - asset turnover
        avg_assets = (balance_sheet['Total Assets'][years[0]] + balance_sheet['Total Assets'][years[1]]) / 2
        avg_assets_py = (balance_sheet['Total Assets'][years[1]] + balance_sheet['Total Assets'][years[2]]) / 2
        at = revenue / avg_assets
        at_py = revenue_py / avg_assets_py
        at_score = 1 if at > at_py else 0

        operating_efficiency_score = gm_score + at_score
        
    # Valuation
        # Score 10 - EV / Ebitda
        market_cap = ticker_obj.info['sharesOutstanding'] * ticker_obj.info['marketCap']  
        total_debt = balance_sheet['Total Debt'][years[0]] 
        cash_and_equivalents = balance_sheet['Cash And Cash Equivalents'][years[0]]
        ev = market_cap + total_debt - cash_and_equivalents
        ebitda = income_statement['EBITDA'][years[0]]
        ee_ratio = ev / ebitda
        valuation_score = 1 if ee_ratio < 16 else 0

    except Exception as e:
        print(f'Something went wrong with {ticker}, {e}')
    total_score = operating_efficiency_score + leverage_score + profitability_score + valuation_score
    return total_score


def get_tickers():
    cleaned_tickers = []
    tickers = sp500()
    for ticker in tickers:
        if get_rating(ticker) > 7:
            cleaned_tickers.append(ticker)
    return cleaned_tickers