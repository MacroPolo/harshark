import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from actions.generic import clearEntriesSearch

class GlobalSearch():
    def __init__(self, app):
        self.app = app
        self.search_string_a = self.app.global_searchbox.text()
        self.search_string_b = self.app.global_searchbox.text().casefold()
        self.column_count = self.app.entries_table.columnCount()
        self.found_rows = []
        self.main()

    def main(self):
        clearEntriesSearch(self.app)

        if not self.search_string_a:
            return
        else:
            self.app.statusbar.showMessage('Searching...')
            search_start = time.time()
            self._searchEntries()
            self._highlightEntries()
            match_count = len(self.found_rows)
            search_stop = time.time()
            elapsed_time = search_stop - search_start

        if self.found_rows:
            self.app.entries_table.selectRow(self.found_rows[0])
            self.app.entries_table.setFocus()
            self.app.next_match_entries.setEnabled(True)
            self.app.clear_match_entries.setEnabled(True)
        
        self.app.statusbar.showMessage('Search Result: Found {} matching entries in {:.1f} seconds.'.format(match_count, elapsed_time))

    def _searchEntries(self):
        for k, v in self.app.har_parsed.items():
            found_item = None
            if self.app.config.getConfig('case-sensitive-matching'):
                if self.search_string_a in str(v):
                    # look for entry ID in table and return QTableWidgetItem
                    found_item = self.app.entries_table.findItems(k, Qt.MatchFlags(Qt.MatchFixedString |
                                                                                   Qt.MatchCaseSensitive |
                                                                                   Qt.MatchWrap))[0]
            else:
                if self.search_string_b in str(v).casefold():
                    # look for entry ID in table and return QTableWidgetItem
                    found_item = self.app.entries_table.findItems(k, Qt.MatchFlags(Qt.MatchFixedString |
                                                                                   Qt.MatchCaseSensitive |
                                                                                   Qt.MatchWrap))[0]
            if found_item:
                found_item_row = self.app.entries_table.row(found_item)
                self.found_rows.append(found_item_row)

    def _highlightEntries(self):
        # TODO Figure out what is going on with this. The default QColor for cell is black 
        # but with a value of 0?
        colour_none = QColor(0, 0, 0).rgb()
        colour_default_hex = self.app.config.getConfig('colour_scheme')['default']
        colour_match_hex = self.app.config.getConfig('colour_scheme')['search_match']
        colour_default = QColor(colour_default_hex).rgb()
        colour_match = QColor(colour_match_hex)

        for row in self.found_rows:
            for column in range(self.column_count):
                cell_colour = self.app.entries_table.item(row, column).background().color().rgb()
                # only colour cells which haven't already been colourized
                if cell_colour == colour_none or cell_colour == colour_default:
                    self.app.entries_table.item(row, column).setBackground(colour_match)

