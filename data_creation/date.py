months = ({
    1: "January",
    1: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
    })

class Date:
    def __init__(self, month="January", day=1, year=2019):
        self.month = months.get(month)
        self.day = day
        self.year = year

    def __str__(self):
        return self.month + " " + str(self.day) + ", " + str(self.year)
