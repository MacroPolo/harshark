#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Harshark: A simple, offline HAR viewer.

Usage:
    $ python3 harshark.py

    The user guide for Harshark can be found on the GitHub page at
    https://github.com/MacroPolo/harshark

"""

import io
import json
import os
import random
import string
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QTextDocument
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QFontDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class TableWidgetItem(QTableWidgetItem):
    """Reimplement QTableWidgetItem to allow numeric sorting of numeric columns."""
    def __init__(self, text, sortKey):
        QTableWidgetItem.__init__(self, text, QTableWidgetItem.UserType)
        self.sortKey = sortKey

    def __lt__(self, other):
        try:
            return self.sortKey < other.sortKey
        except TypeError:
            return -1


class MainApp(QMainWindow):
    """Harshark application UI and logic."""
    def __init__(self):
        super().__init__()
        # display mode for request/response panels [0 = spaced, 1 = compact]
        self.display_mode = 1
        # search result mode [0 = filter, 1 = highlight]
        self.search_mode = 1
        # case sensitive searching [ 0 = case sensitive, 1 = non case sensitive]
        self.case_mode = 1
        # search result highlight colour [yellow]
        self.chosen_colour = QColor(255, 255, 128)
        # number of characters to truncate large body content to
        self.truncate_size = 2000
        # content with any of these MIME-types will be displayed in the body tabs
        self.body_safelist = [
                'text',
                'html',
                'css',
                'json',
                'javascript',
                'js',
                'xml',
                'x-www-form-urlencoded'
        ]
        # display styles for request/response panels
        self.data_styles = ['<b>{}</b><br>{}<br>', '<b>{}</b>: {}']

        # display styles for Cookies
        self.cookie_styles = ['''<b>Name</b><br>{}<br><br>
                              <b>Value</b><br>{}<br><br>
                              <b>Path</b><br>{}<br><br>
                              <b>Domain</b><br>{}<br><br>
                              <b>Expires</b><br>{}<br><br>
                              <b>httpOnly</b><br>{}<br><br>
                              <b>Secure</b><br>{}<br><br>
                              - - -
                              <br>''',
                              '''<b>Name</b>: {}<br>
                              <b>Value</b>: {}<br>
                              <b>Path</b>: {}<br>
                              <b>Domain</b>: {}<br>
                              <b>Expires</b>: {}<br>
                              <b>httpOnly</b>: {}<br>
                              <b>Secure</b>: {}<br>'''
                             ]

        self.initUI()
        

    def initUI(self):
        """Build the PyQt UI."""
        # ---------------------------------------------------------
        # SHORTCUTS
        # ---------------------------------------------------------

        # F5 to loop through search results in request tabs
        self.sc_next_match_request = QShortcut(QKeySequence("F5"), self)
        self.sc_next_match_request.activated.connect(self.nextMatchRequest)

        # F6 to loop through search results in response tabs
        self.sc_next_match_response = QShortcut(QKeySequence("F6"), self)
        self.sc_next_match_response.activated.connect(self.nextMatchResponse)

        # ---------------------------------------------------------
        # ICONS
        # ---------------------------------------------------------

        cwd = os.path.dirname(__file__)

        logo_icon = os.path.join(cwd, '..', 'icons', 'harshark.png')
        about_icon = os.path.join(cwd, '..', 'icons', 'about.png')
        backward_icon = os.path.join(cwd, '..', 'icons', 'backward.png')
        case_icon = os.path.join(cwd, '..', 'icons', 'case.png')
        colour_icon = os.path.join(cwd, '..', 'icons', 'colour.png')
        delete_icon = os.path.join(cwd, '..', 'icons', 'delete.png')
        exit_icon = os.path.join(cwd, '..', 'icons', 'exit.png')
        expand_icon = os.path.join(cwd, '..', 'icons', 'expand.png')
        font_icon = os.path.join(cwd, '..', 'icons', 'font.png')
        forward_icon = os.path.join(cwd, '..', 'icons', 'forward.png')
        open_icon = os.path.join(cwd, '..', 'icons', 'open.png')
        remove_icon = os.path.join(cwd, '..', 'icons', 'remove.png')
        resize_icon = os.path.join(cwd, '..', 'icons', 'resize.png')
        wrap_icon = os.path.join(cwd, '..', 'icons', 'wrap.png')
        
        # ---------------------------------------------------------
        # ACTIONS
        # ---------------------------------------------------------

        # open
        open_act = QAction(QIcon(open_icon), '&Open', self)
        open_act.setShortcut('Ctrl+O')
        open_act.setStatusTip('Open a new HAR file')
        open_act.triggered.connect(self.openFile)

        # quit
        exit_act = QAction(QIcon(exit_icon), '&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit Harshark')
        exit_act.triggered.connect(qApp.quit)

        #font choice
        font_act = QAction(QIcon(font_icon), 'Choose &Font...', self)
        font_act.setStatusTip('Choose the main display font')
        font_act.triggered.connect(self.changeFont)

        #highlight colour choice
        colour_act = QAction(QIcon(colour_icon), 'Choose &Highlight Colour...', self)
        colour_act.setStatusTip('Choose the colour used to highlight search matches')
        colour_act.triggered.connect(self.changeHighlight)
        
        #delete
        delete_act = QAction(QIcon(delete_icon), 'Delete Row', self)
        delete_act.setStatusTip('Delete the selected requests')
        delete_act.setShortcut('Delete')
        delete_act.triggered.connect(self.deleteRow)

        #expand
        expand_act = QAction(QIcon(expand_icon), 'Display all Body Content', self)
        expand_act.setStatusTip('Display all request and response body content for the selected')
        expand_act.setShortcut('Ctrl+X')
        expand_act.triggered.connect(self.expandBody)

        #resize columns to fit
        resize_col_act = QAction(QIcon(resize_icon), 'Resize Columns to Fit', self)
        resize_col_act.setStatusTip('Resize all columns to fit')
        resize_col_act.setShortcut('Ctrl+R')
        resize_col_act.triggered.connect(self.resizeColumns)

        #next match
        next_match_act = QAction(QIcon(forward_icon), 'Next match', self)
        next_match_act.setStatusTip('Go to next match')
        next_match_act.setShortcut('F3')
        next_match_act.triggered.connect(self.nextMatch)

        #previous match
        prev_match_act = QAction(QIcon(backward_icon), 'Previous match', self)
        prev_match_act.setStatusTip('Go to previous match')
        prev_match_act.setShortcut('Shift+F3')
        prev_match_act.triggered.connect(self.previousMatch)

        #clear matches
        clear_match_act = QAction(QIcon(remove_icon), 'Clear Search Results', self)
        clear_match_act.setStatusTip('Clear all search results')
        clear_match_act.triggered.connect(self.clearSearch)

        #toggle case sensitivity
        self.case_act = QAction(QIcon(case_icon), 'Toggle Case Sensitive Matching', 
                                self, checkable=True)
        self.case_act.setChecked(False)
        self.case_act.setStatusTip('Toggle case sensitive matching')
        self.case_act.triggered.connect(self.toggleCase)

        #toggle wordwrap
        wordwrap_act = QAction(QIcon(wrap_icon), 'Toogle Word Wrap', 
                               self, checkable=True)
        wordwrap_act.setChecked(True)
        wordwrap_act.setStatusTip('Toggle word wrap')
        wordwrap_act.setShortcut('Ctrl+W')
        wordwrap_act.triggered.connect(self.toggleWordWrap)

        #about popup
        about_act = QAction(QIcon(about_icon), 'About', self)
        about_act.setStatusTip('Information about Harshark')
        about_act.triggered.connect(self.aboutPopup)
        
        # ---------------------------------------------------------
        # MAIN MENU
        # ---------------------------------------------------------

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        options_menu = menu_bar.addMenu('&Options')
        help_menu = menu_bar.addMenu('&Help')

        file_menu.addAction(open_act)
        file_menu.addAction(exit_act)

        options_menu.addAction(font_act)
        options_menu.addAction(colour_act)

        help_menu.addAction(about_act)
        
        # ---------------------------------------------------------
        # TOOLBARS
        # ---------------------------------------------------------
        
        self.toolbar_actions = self.addToolBar('Tools')
        self.toolbar_search = self.addToolBar('Search & Filter')

        self.toolbar_actions.setIconSize(QSize(20, 20))
        self.toolbar_search.setIconSize(QSize(20, 20))
               
        self.toolbar_search.setFloatable(False)
        self.toolbar_actions.setFloatable(False)
        
        self.displaymode = QComboBox()
        self.displaymode.addItem('Compact')
        self.displaymode.addItem('Spaced')
        self.displaymode.setStatusTip('Choose layout of request/response content')
        self.displaymode.currentIndexChanged.connect(self.displayModeChanged)

        display_mode_lbl = QLabel('Display Mode: ', self)
        display_mode_lbl.setMargin(5)
        
        self.toolbar_actions.addAction(open_act)
        self.toolbar_actions.addSeparator()
        self.toolbar_actions.addAction(delete_act)
        self.toolbar_actions.addAction(resize_col_act)
        self.toolbar_actions.addAction(wordwrap_act)
        self.toolbar_actions.addAction(expand_act)
        self.toolbar_actions.addSeparator()
        self.toolbar_actions.addWidget(display_mode_lbl)
        self.toolbar_actions.addWidget(self.displaymode)

        searchbox_lbl = QLabel('Search: ', self)
        searchbox_lbl.setMargin(5)
        
        self.searchbox = QLineEdit(self)
        self.searchbox.setPlaceholderText('Enter search query here to find matches')
        self.searchbox.setStatusTip('Highlight or filter requests which contain search term')
        self.searchbox.returnPressed.connect(self.searchEntries)

        self.searchmode = QComboBox()
        self.searchmode.addItem('Highlight Results')
        self.searchmode.addItem('Filter Results')
        self.searchmode.setStatusTip('Choose to either hightlight or filter requests which contain search term')
        self.searchmode.currentIndexChanged.connect(self.searchModeChanged)
        
        self.toolbar_search.addWidget(searchbox_lbl)
        self.toolbar_search.addWidget(self.searchbox)
        self.toolbar_search.addWidget(self.searchmode)
        self.toolbar_search.addAction(self.case_act)
        self.toolbar_search.addSeparator()
        self.toolbar_search.addAction(prev_match_act)
        self.toolbar_search.addAction(next_match_act)
        self.toolbar_search.addAction(clear_match_act)

        # ---------------------------------------------------------
        # STATUSBAR
        # ---------------------------------------------------------
        self.status_bar = self.statusBar()

        # ---------------------------------------------------------
        # ENTRY TABLE
        # ---------------------------------------------------------
        header_labels = ['id',
                        'Timestamp',
                        'Request Time',
                        'Server IP',
                        'Request Method',
                        'Request URL',
                        'Response Code',
                        'HTTP Version',
                        'MIME Type',
                        'Request Header Size',
                        'Request Body Size',
                        'Response Header Size',
                        'Response Body Size',
                        ]

        self.entry_table = QTableWidget()
        self.entry_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entry_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entry_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entry_table.setColumnCount(len(header_labels))
        self.entry_table.setHorizontalHeaderLabels(header_labels)
        self.entry_table.hideColumn(0)
        self.entry_table.setFont(QFont('Segoe UI', 10))

        # columns which should be sorted as numbers rather than strings
        self.numeric_columns = [2, 3, 6, 9, 10, 11, 12]

        # when row clicked, fetch the request/response
        self.entry_table.itemSelectionChanged.connect(self.selectRow)

        # ---------------------------------------------------------
        # REQUESTS TAB
        # ---------------------------------------------------------

        self.request_tabs = QTabWidget()

        request_headers_tab = QWidget()
        request_body_tab = QWidget()
        request_query_tab = QWidget()
        request_cookie_tab = QWidget()

        self.request_tabs.addTab(request_headers_tab, 'Headers')
        self.request_tabs.addTab(request_body_tab, 'Body')
        self.request_tabs.addTab(request_query_tab, 'Query Strings')
        self.request_tabs.addTab(request_cookie_tab, 'Cookies')

        self.request_headers_tab_text = QTextEdit()
        self.request_body_tab_text = QTextEdit()
        self.request_query_tab_text = QTextEdit()
        self.request_cookie_tab_text = QTextEdit()

        self.request_headers_tab_text.setAcceptRichText(False)
        self.request_body_tab_text.setAcceptRichText(False)
        self.request_query_tab_text.setAcceptRichText(False)
        self.request_cookie_tab_text.setAcceptRichText(False)

        self.request_headers_tab_text.setReadOnly(True)
        self.request_body_tab_text.setReadOnly(True)
        self.request_query_tab_text.setReadOnly(True)
        self.request_cookie_tab_text.setReadOnly(True)

        self.request_headers_tab_text.setUndoRedoEnabled(False)
        self.request_body_tab_text.setUndoRedoEnabled(False)
        self.request_query_tab_text.setUndoRedoEnabled(False)
        self.request_cookie_tab_text.setUndoRedoEnabled(False)
         
        request_headers_tab_layout = QVBoxLayout()
        request_body_tab_layout = QVBoxLayout()
        request_query_tab_layout = QVBoxLayout()
        request_cookie_tab_layout = QVBoxLayout()

        request_headers_tab_layout.addWidget(self.request_headers_tab_text)
        request_headers_tab.setLayout(request_headers_tab_layout)

        request_body_tab_layout.addWidget(self.request_body_tab_text)
        request_body_tab.setLayout(request_body_tab_layout)

        request_query_tab_layout.addWidget(self.request_query_tab_text)
        request_query_tab.setLayout(request_query_tab_layout)

        request_cookie_tab_layout.addWidget(self.request_cookie_tab_text)
        request_cookie_tab.setLayout(request_cookie_tab_layout)

        # ---------------------------------------------------------
        # RESPONSES TAB
        # ---------------------------------------------------------
        
        self.response_tabs = QTabWidget()

        response_headers_tab = QWidget()
        response_body_tab = QWidget()
        response_cookie_tab = QWidget()

        self.response_tabs.addTab(response_headers_tab, 'Headers')
        self.response_tabs.addTab(response_body_tab, 'Body')
        self.response_tabs.addTab(response_cookie_tab, 'Cookies')

        self.response_headers_tab_text = QTextEdit()
        self.response_body_tab_text = QTextEdit()
        self.response_cookie_tab_text = QTextEdit()

        self.response_headers_tab_text.setReadOnly(True)
        self.response_body_tab_text.setReadOnly(True)
        self.response_cookie_tab_text.setReadOnly(True)

        self.response_headers_tab_text.setAcceptRichText(False)
        self.response_body_tab_text.setAcceptRichText(False)
        self.response_cookie_tab_text.setAcceptRichText(False)

        self.response_headers_tab_text.setUndoRedoEnabled(False)
        self.response_body_tab_text.setUndoRedoEnabled(False)
        self.response_cookie_tab_text.setUndoRedoEnabled(False) 

        response_headers_tab_layout = QVBoxLayout()
        response_body_tab_layout = QVBoxLayout()
        response_cookie_tab_layout = QVBoxLayout()

        response_headers_tab_layout.addWidget(self.response_headers_tab_text)
        response_headers_tab.setLayout(response_headers_tab_layout)

        response_body_tab_layout.addWidget(self.response_body_tab_text)
        response_body_tab.setLayout(response_body_tab_layout)

        response_cookie_tab_layout.addWidget(self.response_cookie_tab_text)
        response_cookie_tab.setLayout(response_cookie_tab_layout)

        # ---------------------------------------------------------
        # GROUPBOX
        # ---------------------------------------------------------

        self.request_searchbox = QLineEdit(self)
        self.response_searchbox = QLineEdit(self)

        self.request_searchbox.setPlaceholderText('Enter search query here to highlight matches')
        self.response_searchbox.setPlaceholderText('Enter search query here to highlight matches')
        
        self.request_searchbox.returnPressed.connect(self.searchRequest)
        self.response_searchbox.returnPressed.connect(self.searchResponse)
    
        request_vbox = QVBoxLayout()
        response_vbox = QVBoxLayout()

        request_vbox.addWidget(self.request_tabs)
        request_vbox.addWidget(self.request_searchbox)

        response_vbox.addWidget(self.response_tabs)
        response_vbox.addWidget(self.response_searchbox)

        request_group_box = QGroupBox(title='Request')
        request_group_box.setLayout(request_vbox)

        response_group_box = QGroupBox(title='Response')
        response_group_box.setLayout(response_vbox)

        # ---------------------------------------------------------
        # WIDGET SPLITTERS
        # ---------------------------------------------------------

        splitter_hor = QSplitter(Qt.Horizontal)
        splitter_hor.addWidget(request_group_box)
        splitter_hor.addWidget(response_group_box)

        splitter_ver = QSplitter(Qt.Vertical)
        splitter_ver.addWidget(self.entry_table)
        splitter_ver.addWidget(splitter_hor)
        splitter_ver.setStretchFactor(0, 2)
        splitter_ver.setStretchFactor(1, 1)

        self.setCentralWidget(splitter_ver)

        # ---------------------------------------------------------
        # MAIN
        # ---------------------------------------------------------
        
        self.showMaximized()
        # app title
        self.setWindowTitle('Harshark | HTTP Archive (HAR) Viewer | v1.0.1')
        # app icon
        self.setWindowIcon(QIcon(logo_icon))
        # update status bar
        self.status_bar.showMessage('Ready')
        # display the app
        self.show()


    def harCheck(self):
        """Perform all HAR file validation here. We want to make sure that the
        HAR file selected can be used and is not malformed in some way.
        """
        # make sure there is an 'entries' key
        try:
            hartest = self.har['log']['entries']
        except KeyError:
            self.status_bar.showMessage('HAR file contains no entries!')
            return(-1)

        # make sure there is at least one entry
        if len(hartest) < 1:
            self.status_bar.showMessage('HAR file contains no entries!')
            return(-1)

        self.harPrepare()

    
    def harPrepare(self):
        """Prepare the UI and data structures for opening a new HAR file."""
        # initalise dictionaries used to store entry details
        self.request_headers_dict = {}
        self.request_body_dict = {}
        self.request_cookies_dict = {}
        self.request_queries_dict = {}
        self.response_headers_dict = {}
        self.response_body_dict = {}
        self.response_cookies_dict = {}

        # clear request/response textboxes
        self.clearTextEdit()

        # clear the search bar
        self.searchbox.setText('')

        # remove search bar stylings
        self.searchbox.setStyleSheet('''
            QLineEdit {
                background-color: rgb(255, 255, 255);
            }
        ''')

        # clear previous rows
        self.entry_table.setRowCount(0)

        # turn off sorting
        self.entry_table.setSortingEnabled(False)
        
        # initialise progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumWidth(250)
        self.progress_bar.setMaximumHeight(17)

        # update status bar
        self.status_bar.clearMessage()
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.setWindowTitle('Harshark | HTTP Archive (HAR) Viewer | {}'.format(self.file_name))
        
        self.harParseEntries()


    def harParseEntries(self):
        """Parse each entry found in the HAR file and add the interesting key
        values to a list. Create a list of lists to be used to populate the 
        entries table. 
        """

        self.table_data = []

        for i, entry in enumerate(self.har['log']['entries']):

            self.row_data = []

            # update process bar every 10 entries
            if i % 10 == 0:
                self.progress_bar.setValue(i / len(self.har['log']['entries']) * 100)
                QApplication.processEvents()

            # create UID for each request
            uid = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
            
            self.row_data.append(uid)
            self.row_data.append(entry.get('startedDateTime', '-'))
            self.row_data.append(entry.get('time', -1))
            self.row_data.append(entry.get('serverIPAddress', -1))
            self.row_data.append(entry.get('request', {}).get('method', '-'))
            self.row_data.append(entry.get('request', {}).get('url', '-'))
            self.row_data.append(entry.get('response', {}).get('status', -1))
            self.row_data.append(entry.get('response', {}).get('httpVersion', '-'))
            self.row_data.append(entry.get('response', {}).get('content', {}).get('mimeType', '-'))
            self.row_data.append(entry.get('request', {}).get('headersSize', -1))
            self.row_data.append(entry.get('request', {}).get('bodySize', -1))
            self.row_data.append(entry.get('response', {}).get('headersSize', -1))
            self.row_data.append(entry.get('response', {}).get('bodySize', -1))
        
            self.table_data.append(self.row_data)

            # fill the request dictionaries
            self.request_headers_dict[uid] = entry.get('request', {}).get('headers', '')
            self.request_body_dict[uid] = entry.get('request', {}).get('postData', '')
            self.request_cookies_dict[uid] = entry.get('request', {}).get('cookies', '')
            self.request_queries_dict[uid] = entry.get('request', {}).get('queryString', '')

            # fill the response dictionaries
            self.response_headers_dict[uid] = entry.get('response', {}).get('headers', '')
            self.response_body_dict[uid] = entry.get('response', {}).get('content', '')
            self.response_cookies_dict[uid] = entry.get('response', {}).get('cookies', '')
             
        self.harPopulateTable()


    def harPopulateTable(self):
        """Populate the entries table with the data found in the table_data list."""
        for i, row_data in enumerate(self.table_data):
            self.entry_table.insertRow(i)
            self.entry_table.setRowHeight(i, 26)

            for j, item in enumerate(row_data):
                # if this column is a numeric column, sort numerically
                if j in self.numeric_columns:
                    # truncate any decimals on 'time' column
                    if j == 2:
                        item = TableWidgetItem(str(int(item)), item)
                        self.entry_table.setItem(i, j, item)
                    else:
                        item = TableWidgetItem(str(item), item)
                        self.entry_table.setItem(i, j, item)
                # if not, sort alphabetically
                else:
                    self.entry_table.setItem(i, j, QTableWidgetItem(str(item)))
        
        self.harComplete()


    def harComplete(self):
        """Cleanup tasks once the HAR file has been parsed and the entries
        table populated.
        """
        # update the statusbar
        self.progress_bar.setValue(100)
        self.status_bar.removeWidget(self.progress_bar)
        self.status_bar.showMessage('HAR file loaded sucessfully')

        # turn on sorting
        self.entry_table.setSortingEnabled(True)

        # resize columns to fit
        self.resizeColumns()


    def openFile(self):
        """File open dialog window"""
        file_name = QFileDialog.getOpenFileName(self, 'Open file')
        self.file_name = file_name[0]
        
        # no file selected
        if not self.file_name:
            return
        
        try:
            with open(self.file_name, 'r', encoding='utf-8-sig') as har:
                self.har = json.load(har)
        except json.decoder.JSONDecodeError:
            self.status_bar.showMessage('Cannot open selected file. Please select a valid HAR file.')
            return
                
        if self.harCheck() == -1:
            return


    def deleteRow(self):
        """Delete the selected rows from the entries table when hitting the 
        'delete' key or clicking the 'delete' button.
        """
        all_selection_groups = self.entry_table.selectedRanges()
        number_of_selection_groups = len(all_selection_groups)

        # for each row selection group (reverse)
        for i in range(number_of_selection_groups, 0, -1):
            # index into this row selection group
            sel_range  = all_selection_groups[number_of_selection_groups - 1]
            # get first row for this selection
            fist_row = sel_range.topRow()
            # get last row for this selection
            last_row = sel_range.bottomRow()
            # delete from first to last row in this selection        
            for j in range(last_row, fist_row - 1, -1):
                self.entry_table.removeRow(j)
            # decrement, to move to next row selection group
            number_of_selection_groups -= 1
        

    def selectRow(self):
        """Populate the request and response details panels when clicking
        on a row in the entries table."""
        # do nothing when there are no rows
        if self.entry_table.currentRow() == -1:
            return

        # get the display style
        active_style = self.data_styles[self.display_mode]

        # clear old data from the text boxes
        self.clearTextEdit()

        # clear any searchbox stylings
        self.request_searchbox.setStyleSheet('''
            QLineEdit {
                background-color: rgb(255, 255, 255);
            }
        ''')
        self.response_searchbox.setStyleSheet('''
            QLineEdit {
                background-color: rgb(255, 255, 255);
            }
        ''')

        # clear the statusbar
        self.status_bar.clearMessage()
        # clear the request/response searchboxes
        self.request_searchbox.setText('')
        self.response_searchbox.setText('')

        # initialise a cookie store
        cookie_list = []

        # get UID from the active row
        row_id = self.entry_table.item(self.entry_table.currentRow(), 0).text()
        
        # retrieve the data for this UID
        request_headers = self.request_headers_dict[row_id]
        request_body = self.request_body_dict[row_id]
        request_cookies = self.request_cookies_dict[row_id]
        request_queries = self.request_queries_dict[row_id]
        response_headers = self.response_headers_dict[row_id]
        response_body = self.response_body_dict[row_id]
        response_cookies = self.response_cookies_dict[row_id]

        # request headers tab
        for item in request_headers:
            entry = active_style.format(item['name'], item['value'])
            self.request_headers_tab_text.append(entry)
            # if request cookies are not itemised specifically in the HAR,
            # extract the information directly from the request header
            if not request_cookies:
                if item['name'] == 'Cookie' or item['name'] == 'cookie':
                    cookie_header = item['value'].split(';')
                    for cookie in cookie_header:
                        self.request_cookie_tab_text.append(cookie.strip())
                        self.request_cookie_tab_text.append('')

        # request body tab
        if request_body:
            # if request body has valid mimeType
            if any(mime in request_body.get('mimeType') for mime in self.body_safelist):
                entry = request_body.get('text', '')[:self.truncate_size]
                # truncate if large body
                if len(entry) == self.truncate_size:
                    entry = '[Request body truncated. Use Ctrl+X to expand.]\n\n' + str(entry)
                self.request_body_tab_text.insertPlainText(str(entry))
            # mimeType is blank
            elif not request_body.get('mimeType'):
                self.request_body_tab_text.insertPlainText('')
            # else if request body has invalid mimeType
            else:
                self.request_body_tab_text.insertPlainText('[Non text data]')  
        
        # request query strings tab
        for item in request_queries:
            entry = active_style.format(item['name'], item['value'])
            self.request_query_tab_text.append(entry)
        
        # request cookies tab
        for item in request_cookies:
            entry = active_style.format(item['name'], item['value'])
            self.request_cookie_tab_text.append(entry)

        # response headers tab
        for item in response_headers:
            entry = active_style.format(item['name'], item['value'])
            self.response_headers_tab_text.append(entry)
            # if response cookies are not itemised specifically in the HAR,
            # extract the information directly from the response header
            if not response_cookies:
                if item['name'] == 'Set-Cookie' or item['name'] == 'set-cookie':
                    # split unique cookies
                    cookie_header = item['value'].split('\n')
                    for cookie in cookie_header:
                        # split params for each cookie
                        cookie_params = cookie.split(';')
                        for param in cookie_params:
                            self.response_cookie_tab_text.append(param.strip())
                        self.response_cookie_tab_text.append('')

        # response body tab
        if response_body:
            # if response body has a valid mimeType
            if any(mime in response_body.get('mimeType') for mime in self.body_safelist):
                entry = response_body.get('text', '')[:self.truncate_size]
                # truncate if large body
                if len(entry) == self.truncate_size:
                    entry = '[Response body truncated. Use Ctrl+X to expand.]\n\n' + str(entry)
                self.response_body_tab_text.insertPlainText(str(entry))
            # mimeType is blank
            elif not response_body.get('mimeType'):
                self.response_body_tab_text.insertPlainText('')
            # else response body has an invalid mimeType
            else:
                self.response_body_tab_text.insertPlainText('[Non text data]')
    
        # response cookies tab
        if response_cookies:
            for item in response_cookies:
                cookie = {}
                cookie['name'] = item.get('name', '')
                cookie['value'] = item.get('value', '')
                cookie['path'] = item.get('path', '')
                cookie['domain'] = item.get('domain', '')
                cookie['expires'] = item.get('expires', '')
                cookie['httpOnly'] = item.get('httpOnly', '')
                cookie['secure'] = item.get('secure', '')
                cookie_list.append(cookie)

            for cookie in cookie_list:
                active_style = self.cookie_styles[self.display_mode]
                entry = active_style.format(cookie['name'], cookie['value'], 
                                            cookie['path'], cookie['domain'], 
                                            cookie['expires'], cookie['httpOnly'],
                                            cookie['secure'])
                self.response_cookie_tab_text.append(entry)

        # scroll all text boxes to the top
        self.request_headers_tab_text.moveCursor(QTextCursor.Start)
        self.request_body_tab_text.moveCursor(QTextCursor.Start)
        self.request_query_tab_text.moveCursor(QTextCursor.Start)
        self.request_cookie_tab_text.moveCursor(QTextCursor.Start)
        self.response_headers_tab_text.moveCursor(QTextCursor.Start)
        self.response_body_tab_text.moveCursor(QTextCursor.Start)
        self.response_cookie_tab_text.moveCursor(QTextCursor.Start)

    
    def expandBody(self):
        """If request/response body has been truncated, use Ctrl+X to 
        show the full text."""
        # if all rows have been removed from entries table do nothing
        if self.entry_table.currentRow() == -1:
            return

        # get row id
        row_id = self.entry_table.item(self.entry_table.currentRow(), 0).text()
        
        # get current body text
        request_body_text = self.request_body_tab_text.toPlainText()        
        response_body_text = self.response_body_tab_text.toPlainText()

        # show full response body if we know it's been truncated
        if '[Response body truncated. Use Ctrl+X to expand.]' in response_body_text:
            response_body = self.response_body_dict[row_id]
            entry = str(response_body['text'])
            self.response_body_tab_text.setPlainText('')
            self.response_body_tab_text.insertPlainText(entry)

        if '[Request body truncated. Use Ctrl+X to expand.]' in request_body_text:
            request_body = self.request_body_dict[row_id]
            entry = str(request_body['text'])
            self.request_body_tab_text.setPlainText('')
            self.request_body_tab_text.insertPlainText(entry)
        

    def changeFont(self):
        """Change the display font used."""
        font, valid = QFontDialog.getFont()
        if valid:
            self.entry_table.setFont(font)         
            self.request_headers_tab_text.setFont(font)
            self.request_body_tab_text.setFont(font)
            self.request_query_tab_text.setFont(font)
            self.request_cookie_tab_text.setFont(font)
            self.response_headers_tab_text.setFont(font)
            self.response_body_tab_text.setFont(font)
            self.response_cookie_tab_text.setFont(font)


    def changeHighlight(self):
        """Change the colour used to highlight search matches."""
        self.chosen_colour = QColorDialog.getColor()
        
        
    def searchModeChanged(self):
        """Set the search mode (highlight or filter)."""
        current_search_mode = self.searchmode.currentText()
        if current_search_mode == 'Highlight Results':
            self.search_mode = 1
        else:
            self.search_mode = 0


    def displayModeChanged(self):
        """Set the display mode (inline or newline)."""
        current_display_mode = self.displaymode.currentText()
        if current_display_mode == 'Compact':
            self.display_mode = 1
        else:
            self.display_mode = 0


    def toggleCase(self):
        """Set the case sensitivity mode for searching."""
        if self.case_act.isChecked() == True:
            self.case_mode = 0
        else:
            self.case_mode = 1
            

    def resizeColumns(self):
        """Resize all columns to fit with the exeption of the URL column
        with is fixed width to improve readability."""
        self.entry_table.resizeColumnsToContents()
        self.entry_table.setColumnWidth(5, 800)


    def toggleWordWrap(self):
        """Set word wrap on/off for requests and response tabs."""
        wr_mode = self.request_headers_tab_text.wordWrapMode()
        if wr_mode == 4:
            self.request_headers_tab_text.setWordWrapMode(QTextOption.NoWrap)
            self.request_body_tab_text.setWordWrapMode(QTextOption.NoWrap)
            self.request_query_tab_text.setWordWrapMode(QTextOption.NoWrap)
            self.request_cookie_tab_text.setWordWrapMode(QTextOption.NoWrap)
            self.response_headers_tab_text.setWordWrapMode(QTextOption.NoWrap)
            self.response_body_tab_text.setWordWrapMode(QTextOption.NoWrap)
            self.response_cookie_tab_text.setWordWrapMode(QTextOption.NoWrap)
        else:
            self.request_headers_tab_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            self.request_body_tab_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            self.request_query_tab_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            self.request_cookie_tab_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            self.response_headers_tab_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            self.response_body_tab_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
            self.response_cookie_tab_text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)


    def clearTextEdit(self):
        """Clear the content from the request/response tabs."""
        self.request_headers_tab_text.setPlainText('')
        self.request_body_tab_text.setPlainText('')
        self.request_query_tab_text.setPlainText('')
        self.request_cookie_tab_text.setPlainText('')
        self.response_headers_tab_text.setPlainText('')
        self.response_body_tab_text.setPlainText('')
        self.response_cookie_tab_text.setPlainText('')

    
    def searchEntries(self):
        """Search all collected data from the HAR file to find matches."""

        # if there aren't any rows in the table do nothing
        row_count = self.entry_table.rowCount()
        if row_count == 0:
            return

        # remove any previous search highlights
        self.clearSearch()

        # check whether we are doing case-sensitive matching
        find_flags = Qt.MatchFlags()
        if self.case_mode == 0:
            find_flags = Qt.MatchCaseSensitive
        else:
            find_flags = Qt.MatchContains

        # get the search string
        search_string = str(self.searchbox.text())
        search_string_lower = search_string.lower()

        # if search string is blank clear out the ordered list of highligted rows
        # and remove searchbox styling
        if not search_string:
            self.matched_ordered = []
            self.searchbox.setStyleSheet('''
                QLineEdit {
                    background-color: rgb(255, 255, 255);
                }
            ''')
            return

        column_count = self.entry_table.columnCount()
        row_count = self.entry_table.rowCount()

        self.status_bar.showMessage('Searching...')

        # look for request/response tabs which contain the search string, 
        # grab the request UID and find the UID in the table to get the 
        # QTableWidgetItem object

        matched_items = []

        for key, value in self.request_headers_dict.items():
            if self.case_mode == 1:
                if search_string_lower in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, find_flags))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, find_flags))
     
        for key, value in self.request_body_dict.items():
            if self.case_mode == 1:
                if search_string_lower in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, find_flags))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, find_flags))
        
        for key, value in self.request_cookies_dict.items():
            if self.case_mode == 1:
                if search_string_lower in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, find_flags))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, find_flags))

        for key, value in self.request_queries_dict.items():
            if self.case_mode == 1:
                if search_string_lower in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, find_flags))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, find_flags))
        
        for key, value in self.response_headers_dict.items():
            if self.case_mode == 1:
                if search_string_lower in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, find_flags))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, find_flags))
        
        for key, value in self.response_body_dict.items():
            if self.case_mode == 1:
                if search_string_lower in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, find_flags))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, find_flags))
        
        for key, value in self.response_cookies_dict.items():
            if self.case_mode == 1:
                if search_string_lower in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, find_flags))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, find_flags))

        # look for any entry table rows which contain the search string and 
        # get the QTableWidgetItem object
        matched_items.append(self.entry_table.findItems(search_string, find_flags))

        # flatten the list of list
        matched_items = [item for sublist in matched_items for item in sublist]

        matched_rows = []

        # get the table row for each matched QTableWidgetItem object
        if matched_items:
            for item in matched_items:
                matched_rows.append(self.entry_table.row(item))
        # no matches
        else:
            self.status_bar.showMessage('No matches found')
            self.clearSearch()
            self.matched_ordered = []
            return

        # remove duplicate rows
        matched_rows = list(set(matched_rows))

        # highlight each cell of each table row where a match was found
        for row in matched_rows:
            for column in range(column_count):
                item = self.entry_table.item(row, column)
                item.setBackground(self.chosen_colour)

        # filter matched rows
        if self.search_mode == 0:
            for row in range(row_count):
                if row not in matched_rows:
                    self.entry_table.setRowHidden(row, True)

        # get an ordered list of all matched rows
        self.matched_ordered = []
        for row in range(row_count):
            item = self.entry_table.item(row, 1)
            if item.background().color() == self.chosen_colour:
                self.matched_ordered.append(row)

        # activate the first row
        self.entry_table.setFocus()
        self.entry_table.setCurrentCell(self.matched_ordered[0], 1)
        self.status_bar.showMessage('Search Complete : {} Matches'.format(len(matched_rows)))

        # set the searchbox styling to indicate a match
        self.searchbox.setStyleSheet('''
            QLineEdit {
                background-color: rgb(175, 255, 175);
            }
        ''')


    def clearSearch(self):
        """Remove any highlight or filter from the entries table."""
        column_count = self.entry_table.columnCount()
        row_count = self.entry_table.rowCount()

        for row in range(row_count):
            # unhide
            self.entry_table.setRowHidden(row, False)
            # remove highlight
            for column in range(column_count):
                item = self.entry_table.item(row, column)
                item.setBackground(QColor(255, 255, 255))

        # remove searchbox styling
        self.searchbox.setStyleSheet('''
            QLineEdit {
                background-color: rgb(255, 255, 255);
            }
        ''')


    def previousMatch(self):
        """Skip back to the previous search match in the entries table."""
        # do nothing if there is there is no matches in the list or if
        # the list hasn't even been initalised (no HAR loaded)
        try:
            if not self.matched_ordered:
                return
        except AttributeError:
            return

        # get current selected row
        current_row = self.entry_table.currentRow()

        for i, row in reversed(list(enumerate(self.matched_ordered))):
            # current row matches a highlighted row
            if row == current_row:
                try:
                    next_row = self.matched_ordered[i - 1]
                    break
                # end of the index
                except IndexError:
                    next_row = self.matched_ordered[len(self.matched_ordered) - 1]
                    break
            # current row does not match a highlighted row
            elif row < current_row:
                next_row = row
                break
            # end of the index
            else:
                next_row = self.matched_ordered[len(self.matched_ordered) - 1]

        self.entry_table.setCurrentCell(next_row, 1)


    def nextMatch(self):
        """Skip forward to the next search match in the entries table."""
        # do nothing if there is there is no matches in the list or if
        # the list hasn't even been initalised (no HAR loaded)
        try:
            if not self.matched_ordered:
                return
        except AttributeError:
            return

        # get current selected row
        current_row = self.entry_table.currentRow()

        for i, row in enumerate(self.matched_ordered):
            # current row matches a highlighted row
            if row == current_row:
                try:
                    next_row = self.matched_ordered[i + 1]
                    break
                # end of the index
                except IndexError:
                    next_row = self.matched_ordered[0]
                    break
            # current row does not match a highlighted row
            elif row > current_row:
                next_row = row
                break
            # end of the index
            else:
                next_row = self.matched_ordered[0]

        self.entry_table.setCurrentCell(next_row, 1)


    def searchRequest(self):
        """Search in the active requests tab."""
        # clear previous searches
        self.clearSearchTabs('req')

        # set current index for stepping through results
        self.current_index_req = 0

        # store the requests tab the search was performed on
        self.active_request_tab = self.request_tabs.currentIndex()

        find_flags = QTextDocument.FindFlags()
        
        # check for case sensitive matching mode
        if self.case_mode == 0:
            find_flags = QTextDocument.FindCaseSensitively
            
        # search string
        search_string = str(self.request_searchbox.text())

        if search_string == '':
            self.clearSearchTabs('req')
            return

        self.status_bar.showMessage('Searching...')

        # get active QTextEdit object
        if self.active_request_tab == 0:
            active_qtextedit = self.request_headers_tab_text
        elif self.active_request_tab == 1:
            active_qtextedit = self.request_body_tab_text
        elif self.active_request_tab == 2:
            active_qtextedit = self.request_query_tab_text
        elif self.active_request_tab == 3:
            active_qtextedit = self.request_cookie_tab_text

        highlight_style = QTextCharFormat()
        highlight_style.setBackground(QBrush(self.chosen_colour))

        self.cursor_locations_req = []

        # move cursor to the start of the QTextEdit box
        active_qtextedit.moveCursor(QTextCursor.Start)

        # for each match, update the style of the selection
        while True:
            matches = active_qtextedit.find(search_string, find_flags)
            if matches:
                qc = active_qtextedit.textCursor()
                if qc.hasSelection():
                    self.cursor_locations_req.append(qc)
                    qc.mergeCharFormat(highlight_style)
            else:
                break

        num_matches = len(self.cursor_locations_req)

        # set searchbox styling to indicate a match
        if num_matches:
            self.request_searchbox.setStyleSheet('''
                QLineEdit {
                    background-color: rgb(175, 255, 175);
                }
            ''')
        else:
            self.request_searchbox.setStyleSheet('''
                QLineEdit {
                    background-color: rgb(255, 255, 255);
                }
            ''')
        
        active_qtextedit.setFocus()
        self.status_bar.showMessage('Search Complete : {} Matches'.format(num_matches))
    
    
    def nextMatchRequest(self):
        """Skip to the next search match in the active request tab."""
        active_tab = self.request_tabs.currentIndex()

        # do nothing if user tries to skip forward on a tab other than the
        # one the latest search was performed on
        try:
            if self.active_request_tab != active_tab:
                return
        except AttributeError:  # there has been no search (F5 with no search)
            return

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.request_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.request_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.request_query_tab_text
        elif active_tab == 3:
            active_qtextedit = self.request_cookie_tab_text

        if len(self.cursor_locations_req) > 0:
            active_qtextedit.setTextCursor(self.cursor_locations_req[self.current_index_req])
            if len(self.cursor_locations_req) - 1 == self.current_index_req:
                self.current_index_req = 0
            else:
                self.current_index_req += 1


    def clearSearchTabs(self, tab_set):
        """Clear any search highlights from the request tabs."""

        req_headers = self.request_headers_tab_text
        req_body = self.request_body_tab_text
        req_query = self.request_query_tab_text
        req_cookie = self.request_cookie_tab_text

        res_headers = self.response_headers_tab_text
        res_body = self.response_body_tab_text
        res_cookies = self.response_cookie_tab_text

        req_tabs = [req_headers, req_body, req_query, req_cookie]
        res_tabs = [res_headers, res_body, res_cookies]

        if tab_set == 'req':
            active_tabs = req_tabs
        elif tab_set == 'res':
            active_tabs = res_tabs

        highlight_style = QTextCharFormat()
        highlight_style.setBackground(QBrush(QColor(255, 255, 255)))

        for tab in active_tabs:
            tab.selectAll()
            cursor = tab.textCursor()
            cursor.mergeCharFormat(highlight_style)

            # reset the cursor
            tab.moveCursor(QTextCursor.Start)
        
        # remove searchbox styling
        if tab_set == 'req':
            self.cursor_locations_req = []
            self.request_searchbox.setStyleSheet('''
                QLineEdit {
                    background-color: rgb(255, 255, 255);
                }
            ''')
        elif tab_set == 'res':
            self.cursor_locations_res = []
            self.response_searchbox.setStyleSheet('''
                QLineEdit {
                    background-color: rgb(255, 255, 255);
                }
            ''')

        self.status_bar.clearMessage()


    def searchResponse(self):
        """Search in the active response tab."""
        # clear previous searches
        self.clearSearchTabs('res')

        # set current index for stepping through results
        self.current_index_res = 0

        # store the response tab the search was performed on
        self.active_response_tab = self.response_tabs.currentIndex()
        
        find_flags = QTextDocument.FindFlags()
        
        # check for case sensitive matching mode
        if self.case_mode == 0:
            find_flags = QTextDocument.FindCaseSensitively
            
        # search string
        search_string = str(self.response_searchbox.text())

        if search_string == '':
            self.clearSearchTabs('res')
            return

        self.status_bar.showMessage('Searching...')

        # get active QTextEdit object
        if self.active_response_tab == 0:
            active_qtextedit = self.response_headers_tab_text
        elif self.active_response_tab == 1:
            active_qtextedit = self.response_body_tab_text
        elif self.active_response_tab == 2:
            active_qtextedit = self.response_cookie_tab_text      

        highlight_style = QTextCharFormat()
        highlight_style.setBackground(QBrush(self.chosen_colour))

        self.cursor_locations_res = []

        # move cursor to the start of the QTextEdit box
        active_qtextedit.moveCursor(QTextCursor.Start)

        while True:
            matches = active_qtextedit.find(search_string, find_flags)
            if matches:
                qc = active_qtextedit.textCursor()
                if qc.hasSelection():
                    self.cursor_locations_res.append(qc)
                    qc.mergeCharFormat(highlight_style)
            else:
                break

        num_matches = len(self.cursor_locations_res)

        # set searchbox styling to indicate a match
        if num_matches:
            self.response_searchbox.setStyleSheet('''
                QLineEdit {
                    background-color: rgb(175, 255, 175);
                }
            ''')
        else:
            self.response_searchbox.setStyleSheet('''
                QLineEdit {
                    background-color: rgb(255, 255, 255);
                }
            ''')

        active_qtextedit.setFocus()        
        self.status_bar.showMessage('Search Complete : {} Matches'.format(num_matches))
        

    def nextMatchResponse(self):
        """Skip to the next search match in the active response tab."""
        active_tab = self.response_tabs.currentIndex()

        # do nothing if user tries to skip forward on a tab other than the
        # one the search was performed on
        try:
            if self.active_response_tab != active_tab:
                return
        except AttributeError:  # there has ben no search (F6 with no search)
            return

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.response_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.response_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.response_cookie_tab_text

        if len(self.cursor_locations_res) > 0:
            active_qtextedit.setTextCursor(self.cursor_locations_res[self.current_index_res])
            if len(self.cursor_locations_res) - 1 == self.current_index_res:
                self.current_index_res = 0
            else:
                self.current_index_res += 1


    def aboutPopup(self):
        """About Harshark popup dialog."""
        about_msg = QMessageBox()
        about_msg.setIcon(QMessageBox.Information)
        about_msg.setWindowTitle("About Harshark")        
        about_msg.setText('Harshark Version 1.0.1\n\nCopyright © 2017 Mark Riddell')
        about_msg.setInformativeText("Sofware licensed under the MIT License.")
        about_msg.exec_()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 10))
    app.setStyle("Fusion")
    main_harshark = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()