import dateutil.parser

def parse(date, dayfirst=False):
    if date[:4].isnumeric():
        return dateutil.parser.parse(date, dayfirst=False)
    else:
        return dateutil.parser.parse(date, dayfirst=True)
