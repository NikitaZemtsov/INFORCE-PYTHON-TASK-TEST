import datetime
import pandas as pd
from inforce import app, docs, logger
from datetime import datetime


def take_date(row_date) -> list:
    if row_date is None:
        print()
        return [datetime.utcnow().date()]
    else:
        dates = [datetime.strptime(date, "%Y-%m-%d").date() for date in row_date.split(",")]
        if len(dates) == 2:
            start_date, end_date = dates
            return list(pd.date_range(start=start_date, end=end_date, freq="D"))
        else:
            return dates
