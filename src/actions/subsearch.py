from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTabWidget

from actions.generic import clearTabSearch

class SubSearch():
    def __init__(self, app, tab_group):
        self.app = app
        self.tab_group = tab_group
        self.matches = []
        self.highlight_style = QTextCharFormat()
        self.main()

    def main(self):
        self._updateBrush()
        clearTabSearch(self.app, tab_group=self.tab_group)
        if self.tab_group == 'request':
            self._searchRequest()
        elif self.tab_group == 'response':
            self._searchResponse()
        else:
            raise Exception # TODO: Naked exceptions...

    def _updateBrush(self):
        colour_match_hex = self.app.config.getConfig('colour_scheme')['search_match']
        colour_match = QColor(colour_match_hex)
        self.highlight_style.setBackground(QBrush(colour_match))

    def _searchRequest(self):

        search_term = self.app.request_filter.text()

        active_tab_index = self.app.request_tabs.currentIndex()
        active_tab_textedit = self.app.request_textedits[active_tab_index]

        request_matches = []

        active_tab_textedit.moveCursor(QTextCursor.Start)

        # for each match, update the style of the selection
        while True:
            match = active_tab_textedit.find(search_term)
            if match:
                cursor = active_tab_textedit.textCursor()
                if cursor.hasSelection():
                    request_matches.append(cursor)
                    cursor.mergeCharFormat(self.highlight_style)
            else:
                break

        match_count = len(request_matches)
        self.app.statusbar.showMessage('Search Result: Found {} matching entries.'.format(match_count))

        if request_matches:
            active_tab_textedit.setTextCursor(request_matches[0])
            active_tab_textedit.setFocus()
            self.matches = request_matches
            self.app.clear_match_request_btn.setEnabled(True)
            self.app.next_match_request_btn.setEnabled(True)

    def _searchResponse(self):

        search_term = self.app.response_filter.text()

        active_tab_index = self.app.response_tabs.currentIndex()
        active_tab_textedit = self.app.response_textedits[active_tab_index]

        response_matches = []

        active_tab_textedit.moveCursor(QTextCursor.Start)

        # for each match, update the style of the selection
        while True:
            match = active_tab_textedit.find(search_term)
            if match:
                cursor = active_tab_textedit.textCursor()
                if cursor.hasSelection():
                    response_matches.append(cursor)
                    cursor.mergeCharFormat(self.highlight_style)
            else:
                break

        match_count = len(response_matches)
        self.app.statusbar.showMessage('Search Result: Found {} matching entries.'.format(match_count))

        if response_matches:
            active_tab_textedit.setTextCursor(response_matches[0])
            active_tab_textedit.setFocus()
            self.matches = response_matches
            self.app.clear_match_response_btn.setEnabled(True)
            self.app.next_match_response_btn.setEnabled(True)
