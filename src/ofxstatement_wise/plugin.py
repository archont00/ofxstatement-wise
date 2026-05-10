import csv
import csv
from datetime import datetime
from typing import Dict, Iterable, Optional
from decimal import Decimal

from ofxstatement import statement
from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser

class WisePlugin(Plugin):
    """Wise Payments Ltd (UK) (exported from Account // Statements: CSV)
    """

    def get_parser(self, filename):
        WisePlugin.encoding = self.settings.get('charset', 'utf-8-sig')
        f = open(filename, "r", encoding=WisePlugin.encoding)
        parser = WiseParser(f)
        parser.statement.currency = self.settings.get('currency', 'EUR')
        parser.statement.bank_id = self.settings.get('bank', 'TRWIBEB1XXX')
        parser.statement.account_id = self.settings.get('account', '')
        parser.statement.account_type = self.settings.get('account_type', 'CHECKING')
        parser.statement.trntype = "OTHER"
        return parser

class WiseParser(CsvStatementParser):

    date_format = '%d-%m-%Y %H:%M:%S.%f'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.columns = None
        self.mappings = None

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        # Field delimiter may be dependent on user settings in mobile App (English/Czech)
        return csv.reader(self.fin, delimiter=',', quotechar='"')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """

        # First line of CSV file contains headers, not an actual transaction
        if self.cur_record == 1:
            # Prepare columns headers lookup table for parsing
            self.columns = {v: i for i,v in enumerate(line)}
            self.mappings = {
                #"date": self.columns['Date Time'],
                "memo": self.columns['Description'],
                #"payee": self.columns['Payee Name'],
                #"check_no": self.columns['TransferWise ID'],
                "id": self.columns['TransferWise ID'],
                "amount": self.columns['Amount'],
            }
            # And skip further processing by parser
            return None

        # Shortcut
        columns = self.columns

        # Normalize string. Better safe than sorry.
        for i,v in enumerate(line):
            line[i] = v.strip()

        StatementLine = super(WiseParser, self).parse_record(line)

        # Ignore lines, which do not have a posting date yet (typically pmts by debit cards are processed with a delay)
        currency = line[columns["Currency"]]
        if currency != self.statement.currency:
            # Skip lines in other currencies
            return None
        else:
            StatementLine.date_user = line[columns["Date Time"]]
            StatementLine.date_user = datetime.strptime(StatementLine.date_user, self.date_format)

        StatementLine.trntype = line[columns["Transaction Type"]]

        # .payee becomes OFX.NAME which becomes "Description" in GnuCash
        # .memo  becomes OFX.MEMO which becomes "Notes"       in GnuCash
        # When .payee is empty, GnuCash imports .memo to "Description" and keeps "Notes" empty

        # StatementLine.memo = "Název protistrany" + "Číslo účtu protistrany" + "Kód banky protistrany" + "IBAN protistrany"

        StatementLine.memo = self._make_memo(line)

        return StatementLine

    def _make_memo(self, line):
        descr = line[self.columns["Description"]]
        payref = line[self.columns["Payment Reference"]]
        exc_from = line[self.columns["Exchange From"]]
        exc_to = line[self.columns["Exchange To"]]
        exc_rate = line[self.columns["Exchange Rate"]]
        card_no = line[self.columns["Card Last Four Digits"]]

        memo = descr

        if payref:
            memo += f" ({payref})"
        if exc_from and exc_to and exc_rate:
            memo += f", {exc_rate} {exc_from}/{exc_to}"
        if card_no:
            memo += f", card #: {card_no}"

        return memo
