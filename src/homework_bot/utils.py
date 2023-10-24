from typing import Union
from datetime import datetime


def check_valid_date(date: Union[str, None]):
    if date is None:
        return True

    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
