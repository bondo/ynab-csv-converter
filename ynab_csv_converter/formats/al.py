import re
from collections import namedtuple

ALLine = namedtuple('ALLine', ['date', 'text', 'amount', 'sender', 'receiver', 'empty'])
amount_pattern = r'^(-| )\d+,\d{2}$'
date_pattern = r'^\d{2}-\d{2}-\d{4}$'
column_patterns = {'date':    date_pattern,
                   'text':    r'^.+$',
                   'amount':  amount_pattern,
                   }
column_patterns = {column: re.compile(regex) for column, regex in column_patterns.items()}
txn_date_descends = True


def getlines(path):
    import csv
    import datetime
    import locale
    from . import validate_line
    from .ynab import YnabLine

    with open(path, 'r', encoding='iso-8859-1') as handle:
        transactions = csv.reader(handle, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_ALL)
        locale.setlocale(locale.LC_ALL, 'da_DK.ISO-8859-1')

        for raw_line in transactions:
            try:
                line = ALLine(*raw_line)
                validate_line(line, column_patterns)

                date = datetime.datetime.strptime(line.date, '%d-%m-%Y')

                payee = line.text
                memo = ''
                if len(line.sender) > 0:
                    payee = line.sender
                    memo = line.text
                if len(line.receiver) > 0:
                    payee = line.receiver
                    memo = line.text

                category = ''

                amount = locale.atof(line.amount)
                if amount > 0:
                    outflow = 0.0
                    inflow = amount
                else:
                    outflow = -amount
                    inflow = 0.0
            except Exception:
                import sys
                msg = ("There was a problem on line {line} in {path}\n"
                       .format(line=transactions.line_num, path=path))
                sys.stderr.write(msg)
                raise

            yield YnabLine(date, payee, category, memo, outflow, inflow)
