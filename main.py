from alp import calc_shares, enter_positions, close_positions
from weights import get_weights
import pandas as pd
from datetime import datetime

def main():
    close_positions()

    today = pd.to_datetime(datetime.now())
    look_back = today - pd.DateOffset(months=4)

    weight_dist = get_weights(look_back, today)
    share_dist = calc_shares(weight_dist)
    enter_positions(share_dist)

if __name__ == '__main__':
    main()