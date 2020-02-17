months = ({
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
    })

class Date:
    def __init__(self, month="January", day=1, year=2019):
        self.month = months.get(month)
        self.day = day
        self.year = year

    def __lt__(self, other):
        if self.year < other.year:
            return True
        elif self.year == other.year:
            if self.month < other.month:
                return True
            elif self.month == other.month:
                if self.day < other.day:
                    return True
        else: return False

    def __gt__(self, other):
        if self.year > other.year:
            return True
        elif self.year == other.year:
            if self.month > other.month:
                return True
            elif self.month == other.month:
                if self.day > other.day:
                    return True
        else: return False

    def __eq__(self, other):
        if self.year == other.year and self.month == other.month and self.day == other.day:
            return True
        else: return False
