from datetime import datetime
from typing import List, Union


def check_valid_dates(dates: List[Union[str, None]]):
    valids = []
    for date in dates:
        if date is None:
            valids.append(True)
            continue

        try:
            datetime.strptime(date, "%Y-%m-%d")
            valids.append(True)
        except ValueError:
            valids.append(False)

    return all(valids)
