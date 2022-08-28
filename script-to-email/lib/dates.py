import datetime
import re
from dateutil.parser import parse


class IncrementalDateGenerator:
    default_interval = datetime.timedelta(days=1)

    def __init__(self, date=None):
        if date:
            if isinstance(date, str):
                if date.startswith('+') or date.startswith('-'):
                    self.date = datetime.datetime.now()
                else:
                    self.date = parse(date)
            else:
                self.date = date
        else:
            self.date = datetime.datetime.now()

    def set_date(self, date: datetime.datetime):
        self.date = date

    def next(self, date=None):
        if isinstance(date, datetime.datetime):
            self.date = date
            return date

        interval = IncrementalDateGenerator.default_interval

        if isinstance(date, str):
            if date.startswith("+") or date.startswith("-"):
                parts = re.findall("([+-]\d)([a-z]+)", date)
                parts = {part[1]: int(part[0]) for part in parts}
                interval = datetime.timedelta(**parts)
                date = self.date
            else:
                date = parse(date)
                interval = None
        else:
            date = self.date

        if interval:
            date = date + interval

        self.date = date

        return self.date
