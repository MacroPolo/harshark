#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Harshark Development Build: A simple, offline HAR viewer.

Usage:
    $ python3 harshark.py

    The user guide can be found at https://github.com/MacroPolo/harshark

"""

import itertools
import os
import sys
from itertools import cycle

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

import configmgr
import style
from actions.columnselectdialog import ColumnSelectDialog
from actions.entryselector import EntrySelector
from actions.fileimporter import FileImporter
from actions.globalsearch import GlobalSearch
from harshark_exceptions import HarImportException
from actions.subsearch import SubSearch
from actions.generic import clearEntriesSearch
from actions.generic import clearTabSearch
from actions.generic import colourizeCells
from actions.generic import decolourizeCells
from actions.generic import expandBody
from actions.generic import resizeColumns


class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.config = configmgr.ConfigMgr()
        self.har_summary = None
        self.har_parsed = None
        self.global_results = None
        self.request_results = None
        self.response_results = None
        self.buildUi()

    def buildUi(self):
        # ---------------------------------------------------------
        # ICONS
        # ---------------------------------------------------------
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons')

        app_icon = QIcon(os.path.join(icon_path, 'crosshairs.svg'))
        open_icon = QIcon(os.path.join(icon_path, 'folder-open.svg'))
        quit_icon = QIcon(os.path.join(icon_path, 'power-off.svg'))
        case_icon = QIcon(os.path.join(icon_path, 'font.svg'))
        next_icon = QIcon(os.path.join(icon_path, 'step-forward.svg'))
        clear_icon = QIcon(os.path.join(icon_path, 'times-circle.svg'))
        resize_icon = QIcon(os.path.join(icon_path, 'arrows-alt-h.svg'))
        wrap_icon = QIcon(os.path.join(icon_path, 'file-alt.svg'))
        sort_icon = QIcon(os.path.join(icon_path, 'sort-alpha-down.svg'))
        colour_icon = QIcon(os.path.join(icon_path, 'paint-brush.svg'))
        saml_icon = QIcon(os.path.join(icon_path, 'exclamation-triangle.svg'))
        self.column_select_icon = QIcon(os.path.join(icon_path, 'columns.svg'))

        # ---------------------------------------------------------
        # MENU BAR
        # ---------------------------------------------------------
        menubar = self.menuBar()
        menubar_file = menubar.addMenu('&File')
        menubar_view = menubar.addMenu('&View')
        menubar_options = menubar.addMenu('&Options')
        menubar_help = menubar.addMenu('&Help')

        # ------------
        # File Menu
        # ------------

        # open file
        action_open = QAction('&Open', self, shortcut='Ctrl+O', icon=open_icon,
                              statusTip='Open a new HAR file')
        action_open.triggered.connect(self.openFile)
        menubar_file.addAction(action_open)

        # quit Harshark
        action_exit = QAction('&Exit', self, shortcut='Ctrl+Q', icon=quit_icon,
                              statusTip='Exit Harshark')
        action_exit.triggered.connect(qApp.quit)
        menubar_file.addAction(action_exit)

        # ------------
        # View Menu
        # ------------

        # word wrap
        self.action_wrap = QAction('&Word Wrap', self, shortcut='ALT+Z', icon=wrap_icon,
                                   checkable=True, statusTip=('Toggle word wrapping for '
                                   'request and response tabs'))

        if self.config.getConfig('word-wrap'):
            self.action_wrap.setChecked(True)

        self.action_wrap.triggered.connect(self.toggleWrap)
        menubar_view.addAction(self.action_wrap)

        # sort request and response headers by name
        self.action_sort = QAction('&Sort Headers', self, shortcut='ALT+S', icon=sort_icon,
                                   checkable=True, statusTip=('Alphabetically sort request '
                                   'and response headers by name'))

        if self.config.getConfig('sort-headers'):
            self.action_sort.setChecked(True)

        self.action_sort.triggered.connect(self.toggleSort)
        menubar_view.addAction(self.action_sort)

        # cell colourizations
        self.action_colourization = QAction('&Cell Colourization', self, shortcut='ALT+C',
                                            icon=colour_icon, checkable=True, 
                                            statusTip=('Toggle cell colourization for cells in '
                                                       'the entries table.'))
        if self.config.getConfig('cell-colorization'):
            self.action_colourization.setChecked(True)

        self.action_colourization.triggered.connect(self.toggleColourization)
        menubar_view.addAction(self.action_colourization)

        # resize columns
        self.action_resize = QAction('&Resize Columns', self, shortcut='ALT+R', icon=resize_icon,
                                     statusTip='Resize columns to fit their contents')
        self.action_resize.triggered.connect(lambda: resizeColumns(self))
        menubar_view.addAction(self.action_resize)

        # ------------
        # Options Menu
        # ------------

        # column selector
        action_columns = QAction('&Choose Columns...', self, icon=self.column_select_icon,
                                 statusTip='Choose which columns to display in the entries table')
        action_columns.triggered.connect(self.columnSelector)
        menubar_options.addAction(action_columns)

        # SAML request and response parsing :: EXPERIMENTAL
        self.action_enable_saml = QAction('SAML Parsing (Experimental)', self, icon=saml_icon,
                                     checkable=True, statusTip=('Enable experimental SAML request '
                                                              'and response parsing. May cause '
                                                              'application crashes.'))
        if self.config.getConfig('experimental-saml'):
            self.action_enable_saml.setChecked(True)

        self.action_enable_saml.triggered.connect(self.toggleSaml)
        menubar_options.addAction(self.action_enable_saml)

        # ---------------------------------------------------------
        # TOOLBARS
        # ---------------------------------------------------------
        toolbar_main = self.addToolBar('Main')
        toolbar_search = self.addToolBar('Search')

        toolbar_main.setFloatable(False)
        toolbar_main.setMovable(False)
        toolbar_main.setIconSize(QSize(18, 18))

        toolbar_search.setFloatable(False)
        toolbar_search.setMovable(False)
        toolbar_search.setIconSize(QSize(18, 18))

        # open file
        toolbar_main.addAction(action_open)

        # case-sensitive searching
        self.toggle_case = QAction('Case sensitive searching', self, checkable=True,
                                   icon=case_icon, toolTip='Toggle case sensitive searching')

        if self.config.getConfig('case-sensitive-matching'):
            self.toggle_case.setChecked(True)
        
        self.toggle_case.triggered.connect(self.toggleCase)
        toolbar_search.addAction(self.toggle_case)

        # global search
        self.global_searchbox = QLineEdit(self, placeholderText='Enter a search query...',
                                          readOnly=True, clearButtonEnabled=True)
        self.global_searchbox.setMaximumWidth(800)
        self.global_searchbox.setMinimumHeight(30)
        self.global_searchbox.setContentsMargins(5, 0, 5, 0)
        self.global_searchbox.returnPressed.connect(self.globalSearch)
        toolbar_search.addWidget(self.global_searchbox)

        # global search: next match
        self.next_match_entries = QAction('Next', self, shortcut='F3', enabled=False,
                                          icon=next_icon, toolTip='Skip forward to next match')
        self.next_match_entries.triggered.connect(self.nextMatchGlobal)
        toolbar_search.addAction(self.next_match_entries)

        # global serach: clear highlights
        self.clear_match_entries = QAction('Clear search', self, enabled=False, icon=clear_icon,
                                           toolTip='Clear search results')
        self.clear_match_entries.triggered.connect(self.clearMatchGlobal)
        toolbar_search.addAction(self.clear_match_entries)

        # ---------------------------------------------------------
        # STATUS BAR
        # ---------------------------------------------------------
        self.statusbar = self.statusBar()

        # ---------------------------------------------------------
        # ENTRIES TABLE
        # ---------------------------------------------------------
        self.entries_table = QTableWidget()
        self.entries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entries_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.entries_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entries_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # select an entry
        self.entries_table.itemSelectionChanged.connect(self.entrySelect)

        # ---------------------------------------------------------
        # REQUEST TABS
        # ---------------------------------------------------------
        self.request_tabs = QTabWidget()

        request_headers_tab = QWidget()
        request_body_tab = QWidget()
        request_query_tab = QWidget()
        request_cookie_tab = QWidget()
        request_saml_tab = QWidget()

        self.request_tabs.addTab(request_headers_tab, 'Headers')
        self.request_tabs.addTab(request_query_tab, 'Parameters')
        self.request_tabs.addTab(request_cookie_tab, 'Cookies')
        self.request_tabs.addTab(request_body_tab, 'Body')
        self.request_tabs.addTab(request_saml_tab, 'SAML')

        self.request_tabs.setTabEnabled(0, False)
        self.request_tabs.setTabEnabled(1, False)
        self.request_tabs.setTabEnabled(2, False)
        self.request_tabs.setTabEnabled(3, False)
        self.request_tabs.setTabEnabled(4, False)

        self.request_headers_tab_text = QTextEdit(readOnly=True)
        self.request_query_tab_text = QTextEdit(readOnly=True)
        self.request_cookie_tab_text = QTextEdit(readOnly=True)
        self.request_body_tab_text = QPlainTextEdit(readOnly=True)
        self.request_saml_tab_text = QPlainTextEdit(readOnly=True)

        # ROBUSTNESS :: We index into this list from a few areas so UI order must be
        # preserved. Can this be made less fragile?
        self.request_textedits = [self.request_headers_tab_text,
                                  self.request_query_tab_text,
                                  self.request_cookie_tab_text,
                                  self.request_body_tab_text,
                                  self.request_saml_tab_text]

        word_wrap = self.config.getConfig('word-wrap')
        for textedit in self.request_textedits:
            if not word_wrap:
                textedit.setWordWrapMode(QTextOption.NoWrap)

        request_headers_tab_layout = QVBoxLayout()
        self.request_body_tab_layout = QVBoxLayout()
        request_query_tab_layout = QVBoxLayout()
        request_cookie_tab_layout = QVBoxLayout()
        request_saml_tab_layout = QVBoxLayout()

        truncate_length = self.config.getConfig('truncate-character-count')
        truncate_button_text = ('Content truncated to {} characters. '
                                'Click to show all content.').format(truncate_length)
        self.request_expand_button = QPushButton(truncate_button_text)
        self.request_expand_button.hide()

        request_headers_tab_layout.addWidget(self.request_headers_tab_text)
        request_headers_tab.setLayout(request_headers_tab_layout)

        self.request_body_tab_layout.addWidget(self.request_expand_button)
        self.request_body_tab_layout.addWidget(self.request_body_tab_text)
        request_body_tab.setLayout(self.request_body_tab_layout)

        request_query_tab_layout.addWidget(self.request_query_tab_text)
        request_query_tab.setLayout(request_query_tab_layout)

        request_cookie_tab_layout.addWidget(self.request_cookie_tab_text)
        request_cookie_tab.setLayout(request_cookie_tab_layout)

        request_saml_tab_layout.addWidget(self.request_saml_tab_text)
        request_saml_tab.setLayout(request_saml_tab_layout)

        # un-truncate request body
        self.request_expand_button.clicked.connect(lambda: expandBody(self, 'request'))

        # clear search highlights on tab change
        self.request_tabs.currentChanged.connect(lambda: self.tabChanged('request'))

        # next match
        self.next_match_request_btn = QPushButton(shortcut='F5', icon=next_icon, enabled=False,
                                                  toolTip='Skip to the next match')
        self.next_match_request_btn.clicked.connect(lambda: self.nextMatchSub('request'))

        # clear highlights
        self.clear_match_request_btn = QPushButton(icon=clear_icon, enabled=False, 
                                                   toolTip='Clear search results')
        self.clear_match_request_btn.clicked.connect(lambda: self.clearMatchSub('request'))

        # ---------------------------------------------------------
        # RESPONSE TABS
        # ---------------------------------------------------------
        self.response_tabs = QTabWidget()

        response_headers_tab = QWidget()
        response_body_tab = QWidget()
        response_cookie_tab = QWidget()
        response_saml_tab = QWidget()

        self.response_tabs.addTab(response_headers_tab, 'Headers')
        self.response_tabs.addTab(response_cookie_tab, 'Cookies')
        self.response_tabs.addTab(response_body_tab, 'Body')
        self.response_tabs.addTab(response_saml_tab, 'SAML')

        self.response_tabs.setTabEnabled(0, False)
        self.response_tabs.setTabEnabled(1, False)
        self.response_tabs.setTabEnabled(2, False)
        self.response_tabs.setTabEnabled(3, False)

        self.response_headers_tab_text = QTextEdit(readOnly=True)
        self.response_cookie_tab_text = QTextEdit(readOnly=True)
        self.response_body_tab_text = QPlainTextEdit(readOnly=True)
        self.response_saml_tab_text = QPlainTextEdit(readOnly=True)

        # ROBUSTNESS :: We index into this list from a few areas so UI order must be
        # preserved. Can this be made less fragile?
        self.response_textedits = [self.response_headers_tab_text,
                                   self.response_cookie_tab_text,
                                   self.response_body_tab_text,
                                   self.response_saml_tab_text]

        for textedit in self.response_textedits:
            if not word_wrap:
                textedit.setWordWrapMode(QTextOption.NoWrap)

        response_headers_tab_layout = QVBoxLayout()
        self.response_body_tab_layout = QVBoxLayout()
        response_cookie_tab_layout = QVBoxLayout()
        response_saml_tab_layout = QVBoxLayout()

        self.response_expand_button = QPushButton(truncate_button_text)
        self.response_expand_button.hide()

        response_headers_tab_layout.addWidget(self.response_headers_tab_text)
        response_headers_tab.setLayout(response_headers_tab_layout)

        self.response_body_tab_layout.addWidget(self.response_expand_button)
        self.response_body_tab_layout.addWidget(self.response_body_tab_text)
        response_body_tab.setLayout(self.response_body_tab_layout)

        response_cookie_tab_layout.addWidget(self.response_cookie_tab_text)
        response_cookie_tab.setLayout(response_cookie_tab_layout)

        response_saml_tab_layout.addWidget(self.response_saml_tab_text)
        response_saml_tab.setLayout(response_saml_tab_layout)

        # un-truncate response body
        self.response_expand_button.clicked.connect(lambda: expandBody(self, 'response'))

        # clear search highlights on tab change
        self.response_tabs.currentChanged.connect(lambda: self.tabChanged('response'))

        # next match
        self.next_match_response_btn = QPushButton(shortcut='F6', icon=next_icon, enabled=False,
                                                  toolTip='Skip to the next match')
        self.next_match_response_btn.clicked.connect(lambda: self.nextMatchSub('response'))

        # clear highlights
        self.clear_match_response_btn = QPushButton(icon=clear_icon, enabled=False, 
                                                   toolTip='Clear search results')
        self.clear_match_response_btn.clicked.connect(lambda: self.clearMatchSub('response'))

        # ---------------------------------------------------------
        # REQUEST / RESPONSE FILTER
        # ---------------------------------------------------------
        self.request_filter = QLineEdit(self, placeholderText='Enter search query...', 
                                        readOnly=True, clearButtonEnabled=True)
        self.request_filter.returnPressed.connect(lambda: self.subSearch('request'))
        self.request_filter.setMinimumHeight(30)

        self.response_filter = QLineEdit(self, placeholderText='Enter search query...',
                                         readOnly=True, clearButtonEnabled=True)
        self.response_filter.returnPressed.connect(lambda: self.subSearch('response'))
        self.response_filter.setMinimumHeight(30)

        # ---------------------------------------------------------
        # REQUEST / RESPONSE LAYOUT
        # ---------------------------------------------------------
        request_vbox = QVBoxLayout()
        request_hbox = QHBoxLayout()
        response_vbox = QVBoxLayout()
        response_hbox = QHBoxLayout()

        request_hbox.addWidget(self.request_filter)
        request_hbox.addWidget(self.next_match_request_btn)
        request_hbox.addWidget(self.clear_match_request_btn)
        
        request_vbox.addWidget(self.request_tabs)
        request_vbox.addLayout(request_hbox)

        response_hbox.addWidget(self.response_filter)
        response_hbox.addWidget(self.next_match_response_btn)
        response_hbox.addWidget(self.clear_match_response_btn)

        response_vbox.addWidget(self.response_tabs)
        response_vbox.addLayout(response_hbox)

        request_group_box = QGroupBox(title='Request Details')
        request_group_box.setLayout(request_vbox)

        response_group_box = QGroupBox(title='Response Details')
        response_group_box.setLayout(response_vbox)

        # ---------------------------------------------------------
        # MAIN WIDGET SPLITTER
        # ---------------------------------------------------------
        splitter_h = QSplitter(Qt.Horizontal)
        splitter_h.addWidget(request_group_box)
        splitter_h.addWidget(response_group_box)

        splitter_v = QSplitter(Qt.Vertical)
        splitter_v.addWidget(self.entries_table)
        splitter_v.addWidget(splitter_h)
        
        # (index, stretch factor)
        #splitter_v.setStretchFactor(0, 1)
        #splitter_v.setStretchFactor(1, 1)

        self.setCentralWidget(splitter_v)

        # ---------------------------------------------------------
        # STYLE
        # ---------------------------------------------------------
        style.setStyleSheet(self, 'light')

        # ---------------------------------------------------------
        # KICKUP
        # ---------------------------------------------------------
        self.setWindowTitle('Harshark 2.0.0 (dev) | HTTP Archive (HAR) Viewer')
        self.setWindowIcon(app_icon)
        self.showMaximized()
        self.show()

    def openFile(self):
        try:
            FileImporter(self)
        except HarImportException:
            return()

    def columnSelector(self):
        ColumnSelectDialog(self)

    def entrySelect(self):
        if self.entries_table.currentRow() > -1:
            EntrySelector(self)

    def toggleCase(self):
        current = self.config.getConfig('case-sensitive-matching')
        self.config.setConfig('case-sensitive-matching', not current)

    def toggleWrap(self):
        current = self.config.getConfig('word-wrap')
        self.config.setConfig('word-wrap', not current)

        for req_textedit, res_textedit in itertools.zip_longest(self.request_textedits,
                                                                self.response_textedits):
            try:
                if not current:
                    req_textedit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
                    res_textedit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
                else:
                    req_textedit.setWordWrapMode(QTextOption.NoWrap)
                    res_textedit.setWordWrapMode(QTextOption.NoWrap)
            except AttributeError:
                break

    def toggleSort(self):
        current = self.config.getConfig('sort-headers')
        self.config.setConfig('sort-headers', not current)
        self.entrySelect()

    def toggleColourization(self):
        current = self.config.getConfig('cell-colorization')
        self.config.setConfig('cell-colorization', not current)
        if current:
            decolourizeCells(self)
        else:
            colourizeCells(self)

    def toggleSaml(self):
        current = self.config.getConfig('experimental-saml')
        self.config.setConfig('experimental-saml', not current)
        if not current:
            self.statusbar.showMessage('Experimental SAML parsing has been enabled. '
                                        'Please re-open the HAR file.')

    def globalSearch(self):
        search_results = GlobalSearch(self).found_rows
        if search_results:
            # move the first match to the end of the list so that the next row selected is 
            # actually the next row and not the current row.
            search_results.append(search_results.pop(0))
            self.global_results = cycle(search_results)

    def nextMatchGlobal(self):
        next_row = next(self.global_results)
        self.entries_table.selectRow(next_row)
        self.entries_table.setFocus()

    def clearMatchGlobal(self):
        clearEntriesSearch(self)
        self.global_searchbox.setText('')

    def tabChanged(self, tab_group):
        clearTabSearch(self, tab_group=tab_group)

    def subSearch(self, tab_group):
        search_results = SubSearch(self, tab_group).matches
        if search_results:
            # move the first match to the end of the list so that the next row selected is 
            # actually the next row and not the current row.
            search_results.append(search_results.pop(0))
            if tab_group == 'request':
                self.request_results = cycle(search_results)
            elif tab_group == 'response':
                self.response_results = cycle(search_results)

    def clearMatchSub(self, tab_group):
        clearTabSearch(self, tab_group=tab_group)
        if tab_group == 'request':
            self.request_filter.setText('')
        elif tab_group == 'response':
            self.response_filter.setText('')

    def nextMatchSub(self, tab_group):
        if tab_group == 'request':
            next_match = next(self.request_results)
            active_tab_index = self.request_tabs.currentIndex()
            active_tab_textedit = self.request_textedits[active_tab_index]
        elif tab_group == 'response':
            next_match = next(self.response_results)
            active_tab_index = self.response_tabs.currentIndex()
            active_tab_textedit = self.response_textedits[active_tab_index]

        active_tab_textedit.setTextCursor(next_match)
        active_tab_textedit.setFocus()

def main():
    app = QApplication(sys.argv)
    main_harshark = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
