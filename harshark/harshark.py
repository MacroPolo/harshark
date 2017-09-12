import json
import random
import string
import sys
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextOption
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QFontDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QActionGroup
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.display_mode = 1
        self.search_mode = 1
        self.case_mode = 1  
        self.initUI()
        
    def initUI(self):

        # ---------------------------------------------------------
        # ACTIONS
        # ---------------------------------------------------------

        # open
        open_act = QAction(QIcon('..\images\open.png'), '&Open', self)
        open_act.setShortcut('Ctrl+O')
        open_act.setStatusTip('Open a new HAR file')
        open_act.triggered.connect(self.openFile)
        
        #delete
        delete_act = QAction(QIcon('..\images\delete.png'), '&Delete Entry', self)
        delete_act.setStatusTip('Delete the selected requests')
        delete_act.setShortcut('Delete')
        delete_act.triggered.connect(self.deleteRow)

        #expand
        expand_act = QAction(QIcon('..\images\expand.png'), 'Expand Response Body', self)
        expand_act.setStatusTip('Show full response body content')
        expand_act.setShortcut('Ctrl+X')
        expand_act.triggered.connect(self.expandBody)

        #font choice
        font_act = QAction(QIcon('..\images\\font.png'), 'Select &Font...', self)
        font_act.setStatusTip('Change the font used to display request/response information')        
        font_act.triggered.connect(self.changeFont)

        #resize columns to fit
        resize_col_act = QAction(QIcon('..\images\\resize.png'), '&Resize Columns to Fit', self)
        resize_col_act.setStatusTip('Resize all columns to fit')
        resize_col_act.setShortcut('Ctrl+R')
        resize_col_act.triggered.connect(self.resizeColumns)

        #toggle wordwrap
        wordwrap_act = QAction(QIcon('..\images\\wrap.png'), '&Toogle Word Wrap', 
                               self, checkable=True)
        wordwrap_act.setChecked(True)
        wordwrap_act.setStatusTip('Toggle word wrap')
        wordwrap_act.setShortcut('Ctrl+W')
        wordwrap_act.triggered.connect(self.toggleWordWrap)

        #next match
        next_match_act = QAction(QIcon('..\images\\forward.png'), '&Next match', self)
        next_match_act.setStatusTip('Goto next match')
        next_match_act.setShortcut('F3')
        next_match_act.triggered.connect(self.nextMatch)

        #next match request
        next_match_request_act = QAction(QIcon('..\images\\forward.png'), 'Next match Request', self)
        next_match_request_act.setStatusTip('Goto next match')
        next_match_request_act.setShortcut('F5')
        next_match_request_act.triggered.connect(self.nextMatchRequest)

        #next match response
        next_match_response_act = QAction(QIcon('..\images\\forward.png'), 'Next match Response', self)
        next_match_response_act.setStatusTip('Goto next match')
        next_match_response_act.setShortcut('F6')
        next_match_response_act.triggered.connect(self.nextMatchResponse)

        #previous match
        prev_match_act = QAction(QIcon('..\images\\backward.png'), '&Previous match', self)
        prev_match_act.setStatusTip('Goto previous match')
        prev_match_act.setShortcut('F4')
        prev_match_act.triggered.connect(self.previousMatch)

        #clear matches
        clear_match_act = QAction(QIcon('..\images\delete.png'), 'Clear Search', self)
        clear_match_act.setStatusTip('Clear all search results')
        clear_match_act.triggered.connect(self.clearSearch)

        #toggle case sensitivity
        self.case_act = QAction(QIcon('..\images\case.png'), 'Toggle Case Sensitive Match', 
                           self, checkable=True)
        self.case_act.setChecked(False)                           
        self.case_act.setStatusTip('Toggle case sensitive matching')
        self.case_act.triggered.connect(self.toggleCase)

        # quit
        exit_act = QAction(QIcon('..\images\exit.png'), '&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit Harshark')
        exit_act.triggered.connect(qApp.quit)
        
        # ---------------------------------------------------------
        # MAIN MENU
        # ---------------------------------------------------------

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        options_menu = menu_bar.addMenu('&Options')
      
        file_menu.addAction(open_act)
        file_menu.addAction(exit_act)

        options_menu.addAction(font_act)

        # ---------------------------------------------------------
        # TOOLBARS
        # ---------------------------------------------------------
        
        self.toolbar_actions = self.addToolBar('Useful commands')
        self.toolbar_search = self.addToolBar('Search & Filter')  
               
        self.toolbar_search.setFloatable(False)
        self.toolbar_actions.setFloatable(False)
        
        self.displaymode = QComboBox()
        self.displaymode.addItem('Compact')
        self.displaymode.addItem('Spaced')
        self.displaymode.currentIndexChanged.connect(self.displayModeChanged)

        display_mode_lbl = QLabel('Display Mode: ', self)
        
        self.toolbar_actions.addAction(open_act)
        self.toolbar_actions.addAction(delete_act)
        self.toolbar_actions.addAction(expand_act)
        self.toolbar_actions.addAction(wordwrap_act)
        self.toolbar_actions.addAction(resize_col_act)
        self.toolbar_actions.addSeparator()
        self.toolbar_actions.addWidget(display_mode_lbl)            
        self.toolbar_actions.addWidget(self.displaymode)
        
        searchbox_lbl = QLabel('Search Filter', self)
        searchbox_lbl.setMargin(5)
        
        self.searchbox = QLineEdit(self)
        self.searchbox.setPlaceholderText('Enter search query here to highlight matches')
        self.searchbox.returnPressed.connect(self.searchEntries)

        self.searchmode = QComboBox()
        self.searchmode.addItem('Highlight Results')        
        self.searchmode.addItem('Filter Results')
        self.searchmode.currentIndexChanged.connect(self.searchModeChanged)
        
        self.toolbar_search.addWidget(searchbox_lbl)
        self.toolbar_search.addWidget(self.searchbox)
        self.toolbar_search.addWidget(self.searchmode)
        self.toolbar_search.addAction(self.case_act)        
        self.toolbar_search.addSeparator()        
        self.toolbar_search.addAction(prev_match_act)
        self.toolbar_search.addAction(next_match_act)
        self.toolbar_search.addAction(clear_match_act)
        self.toolbar_search.addAction(next_match_request_act)
        self.toolbar_search.addAction(next_match_response_act)

        # ---------------------------------------------------------
        # STATUSBAR
        # ---------------------------------------------------------
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

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
                        'Mime Type',
                        'Request Header Size',
                        'Request Body Size',
                        'Response Header Size',
                        'Response Body Size',
                        ]

        self.entry_table = QTableWidget()
        # self.entry_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.entry_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entry_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entry_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entry_table.setColumnCount(len(header_labels))
        self.entry_table.setHorizontalHeaderLabels(header_labels)
        self.entry_table.hideColumn(0)
        self.entry_table.setFont(QFont('Segoe UI', 10))

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

        request_group_box = QGroupBox(title='Requests')
        request_group_box.setLayout(request_vbox)

        response_group_box = QGroupBox(title='Responses')
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

        self.setCentralWidget(splitter_ver)

        # ---------------------------------------------------------
        # MAIN
        # ---------------------------------------------------------
        
        self.showMaximized()
        # app title
        self.setWindowTitle('Harshark | HTTP Archive (HAR) Viewer | v0.3')
        # app icon
        self.setWindowIcon(QIcon('..\images\logo2.png'))
        # display the app
        self.show()


    def openFile(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')
        file_name = file_name[0]
        
        # no file selected
        if file_name == '':
            return()
        else:
        # load the HAR file
            try:
                with open(file_name, encoding='utf-8') as har:
                    self.har = json.load(har)
                    self.harParse()
            except json.decoder.JSONDecodeError:
                self.status_bar.removeWidget(self.progress_bar)
                self.status_bar.showMessage('Invalid file')
                return()


    def harCheck(self):
        try:
            foo = self.har['log']['entries']
        except:
            print('HAR file does not contain any entries')
            self.status_bar.removeWidget(self.progress_bar)
            self.status_bar.showMessage('HAR file contains no entries!')
            return(-1)
        if len(foo) < 1:
            self.status_bar.removeWidget(self.progress_bar)
            self.status_bar.showMessage('HAR file contains no entries!')
            return(-1)


    def harParse(self):

        # initalise dictionaries used to store entry details
        self.request_headers_dict = {}
        self.request_body_dict = {}
        self.request_cookies_dict = {}
        self.request_queries_dict = {}
        self.response_headers_dict = {}
        self.response_body_dict = {}
        self.response_cookies_dict = {}

        # clear any old entries from textboxes
        self.clearTextEdit()

        # clear ny old entries in search bar
        self.searchbox.setText('')

        # columns which should be sorted as numbers rather than strings
        numeric_columns = [2, 3, 6, 9, 10, 11, 12]

        # HAR file none types
        self.none_types = [None, '']

        # remove any previous rows which may exist from a previous file
        self.entry_table.setRowCount(0)

        # turn off sorting
        self.entry_table.setSortingEnabled(False)
        
        # initialise progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumWidth(250)
        self.progress_bar.setMaximumHeight(17)

        # update status bar
        self.status_bar.clearMessage()
        self.status_bar.addWidget(self.progress_bar)

        # make sure we have some entries in the HAR
        har_status = self.harCheck()
        if har_status == -1:
            return()
   
        # for each entry in the HAR file
        for i, entry in enumerate(self.har['log']['entries']):

            # occasionally update the import progress bar
            if i % 10 == 0:
                QApplication.processEvents()
                self.progress_bar.setValue(i / len(self.har['log']['entries']) * 100)

            # create UID for each request
            id = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
            
            # create list of this rows data
            row_data = []

            row_data.append(id)

            try:
                if entry['startedDateTime'] in self.none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['startedDateTime'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['time'] in self.none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['time'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['serverIPAddress'] in self.none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['serverIPAddress'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['request']['method'] in self.none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['request']['method'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['request']['url'] in self.none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['request']['url'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['response']['status'] in self.none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['response']['status'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['response']['httpVersion'] in self.none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['response']['httpVersion'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['response']['content']['mimeType'] in self.none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['response']['content']['mimeType'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['request']['headersSize'] in self.none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['request']['headersSize'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['request']['bodySize'] in self.none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['request']['bodySize'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['response']['headersSize'] in self.none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['response']['headersSize'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['response']['bodySize'] in self.none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['response']['bodySize'])
            except KeyError:
                row_data.append(-1)

            # populate the entries table
            self.entry_table.insertRow(i)

            for j, item in enumerate(row_data):

                # if this column is a numeric column, sort numerically
                if j in numeric_columns:
                    # truncate any decimal 
                    if j == 2:
                        item = TableWidgetItem(str(int(item)), item)
                        self.entry_table.setItem(i, j, item)
                    else:
                        item = TableWidgetItem(str(item), item)
                        self.entry_table.setItem(i, j, item)
                # if not, sort alphabetically
                else:
                    self.entry_table.setItem(i, j, QTableWidgetItem(str(item)))
            
            # fill the requests dictionaries
            try:
                self.request_headers_dict[id] = entry['request']['headers']
            except KeyError:
                self.request_headers_dict[id] = ''
            try:
                self.request_body_dict[id] = entry['request']['postData']
            except KeyError:
                self.request_body_dict[id] = ''
            try:
                self.request_cookies_dict[id] = entry['request']['cookies']
            except KeyError:
                self.request_cookies_dict[id] = ''
            try:
                self.request_queries_dict[id] = entry['request']['queryString']
            except KeyError:
                self.request_queries_dict[id] = ''

            # fill the response dictionaries
            try:
                self.response_headers_dict[id] = entry['response']['headers']
            except KeyError:
                self.response_headers_dict[id] = ''
            try:
                self.response_body_dict[id] = entry['response']['content']
            except KeyError:
                self.response_body_dict[id] = ''
            try:
                self.response_cookies_dict[id] = entry['response']['cookies']
            except:
                self.response_cookies_dict[id] = ''

        # update the statusbar on success
        self.progress_bar.setValue(100)
        self.status_bar.removeWidget(self.progress_bar)
        self.status_bar.showMessage('HAR loaded sucessfully')

        # turn on sorting
        self.entry_table.setSortingEnabled(True)

        # resize columns to fit
        self.resizeColumns()


    def deleteRow(self):
        """delete the selected rows from the requests table when hitting the 
        'delete' key
        """
        all_selection_groups = self.entry_table.selectedRanges()
        # count number of row selection groups
        number_of_selection_groups = len(all_selection_groups)
        # for each row selection group
        for i in range(number_of_selection_groups, 0, -1):
            # index into this row selection group
            selRange  = all_selection_groups[number_of_selection_groups - 1]
            # get first row for this selection
            fist_row = selRange.topRow()
            # get last row for this selection
            last_row = selRange.bottomRow()
            # delete from first to last row in this selection        
            for j in range(last_row, fist_row - 1, -1):
                self.entry_table.removeRow(j)
            # decrement, to move to next row selection group
            number_of_selection_groups -= 1
        

    def selectRow(self):

        # catch when all rows have been deleted
        if self.entry_table.currentRow() == -1:
            return

        # number of characters to truncate large response bodies to
        truncate_size = 2000

        # response body mime-types which will be displayed
        body_safelist = [
                'text', 
                'html',
                'css',
                'json',
                'javascript',
                'js',
                'xml',
                'x-www-form-urlencoded'
        ]

        # cookie store
        cookie_list = []

        # newline name value style
        data_styles = ['<b>{}</b><br>{}<br>', '<b>{}</b>: {}']
        active_style = data_styles[self.display_mode]

        # clear old data from the text boxes
        self.clearTextEdit()

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

            # parse the 'cookie' header in request header if they haven't 
            # been split out into the 'cookies' key in the HAR file
            if not request_cookies:
                if item['name'] == 'Cookie' or item['name'] == 'cookie':
                    cookie_header = item['value'].split(';')
                    for cookie in cookie_header:
                        self.request_cookie_tab_text.append(cookie.strip())
                        self.request_cookie_tab_text.append('')

        # request body tab
        if request_body not in self.none_types:
            if any(mime in request_body['mimeType'] for mime in body_safelist):
                try:
                    entry = request_body['text'][:truncate_size]
                    if len(entry) == truncate_size:
                        entry = '[Request body truncated. Use Ctrl+X to expand.]\n\n' + str(entry)
                    self.request_body_tab_text.insertPlainText(str(entry))
                except KeyError:
                    self.request_body_tab_text.insertPlainText('')
            elif request_body['mimeType'] in self.none_types:
                self.request_body_tab_text.insertPlainText('')
            else:
                self.request_body_tab_text.insertPlainText('[Non text data]')  
        else:
            self.request_body_tab_text.insertPlainText('')  
        
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

            # parse the 'set-cookie' header in response header if they haven't 
            # been split out into the 'cookies' key in the HAR file
            if not response_cookies:
                if item['name'] == 'Set-Cookie' or item['name'] == 'set-cookie':
                    cookie_header = item['value'].split('\n')
                    for cookie in cookie_header:
                        cookie = cookie.split(';')
                        for each in cookie:
                            self.response_cookie_tab_text.append(each.strip())
                        self.response_cookie_tab_text.append('')

        # response body tab
        if response_body not in self.none_types:
            if any(mime in response_body['mimeType'] for mime in body_safelist):
                try:
                    entry = response_body['text'][:truncate_size]
                    if len(entry) == truncate_size:
                        entry = '[Response body truncated. Use Ctrl+X to expand.]\n\n' + str(entry)
                    self.response_body_tab_text.insertPlainText(entry)
                except KeyError:
                    self.response_body_tab_text.insertPlainText('')
            elif response_body['mimeType'] in self.none_types:
                self.response_body_tab_text.insertPlainText('')
            else:
                self.response_body_tab_text.insertPlainText('[Non text data]')
        else:
            self.response_body_tab_text.insertPlainText('')
    
        # response cookies tab
        if response_cookies:
            for item in response_cookies:
                
                cookie = {
                    'name':'',
                    'value':'',
                    'path':'',
                    'domain':'',
                    'expires':'',
                    'httpOnly':'',
                    'secure':'' 
                    }

                try:
                    cookie['name'] = item['name']
                except KeyError:
                    pass
                try:
                    cookie['value'] = item['value']
                except KeyError:
                    pass
                try:
                    cookie['path'] = item['path']
                except KeyError:
                    pass
                try:
                    cookie['domain'] = item['domain']
                except KeyError:
                    pass
                try:
                    cookie['expires'] = item['expires']
                except KeyError:
                    pass
                try:
                    cookie['httpOnly'] = item['httpOnly']
                except KeyError:
                    pass
                try:
                    cookie['secure'] = item['secure']
                except KeyError:
                    pass

                cookie_list.append(cookie)

            for cookie in cookie_list:
                cookie_style_newline = '''<b>Name</b><br>{}<br><br>
                                          <b>Value</b><br>{}<br><br>
                                          <b>Path</b><br>{}<br><br>
                                          <b>Domain</b><br>{}<br><br>
                                          <b>Expires</b><br>{}<br><br>
                                          <b>httpOnly</b><br>{}<br><br>
                                          <b>Secure</b><br>{}<br><br>
                                          - - -
                                          <br>'''

                cookie_style_inline = '''<b>Name</b>: {}<br>
                                         <b>Value</b>: {}<br>
                                         <b>Path</b>: {}<br>
                                         <b>Domain</b>: {}<br>
                                         <b>Expires</b>: {}<br>
                                         <b>httpOnly</b>: {}<br>
                                         <b>Secure</b>: {}<br>'''

                cookie_styles = [cookie_style_newline, cookie_style_inline]
                active_style = cookie_styles[self.display_mode]
                
                entry = active_style.format(cookie['name'], cookie['value'], 
                                            cookie['path'], cookie['domain'], 
                                            cookie['expires'], cookie['httpOnly'],
                                            cookie['secure'])

                self.response_cookie_tab_text.append(entry)
        
        self.scrollTextEdit()


    def scrollTextEdit(self):
        self.request_headers_tab_text.moveCursor(QTextCursor.Start)
        self.request_body_tab_text.moveCursor(QTextCursor.Start)
        self.request_query_tab_text.moveCursor(QTextCursor.Start)
        self.request_cookie_tab_text.moveCursor(QTextCursor.Start)
        self.response_headers_tab_text.moveCursor(QTextCursor.Start)
        self.response_body_tab_text.moveCursor(QTextCursor.Start)
        self.response_cookie_tab_text.moveCursor(QTextCursor.Start)
                
    
    def expandBody(self):

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


    def searchModeChanged(self):
        current_search_mode = self.searchmode.currentText()
        if current_search_mode == 'Highlight Results':
            self.search_mode = 1
        elif current_search_mode == 'Filter Results':
            self.search_mode = 0


    def displayModeChanged(self):
        current_display_mode = self.displaymode.currentText()
        if current_display_mode == 'Compact':
            self.display_mode = 1
        elif current_display_mode == 'Spaced':
            self.display_mode = 0


    def toggleCase(self):
        if self.case_act.isChecked() == True:
            self.case_mode = 0
        else:
            self.case_mode = 1
            

    def resizeColumns(self):
        self.entry_table.resizeColumnsToContents()
        # overwrite URL column sizing
        self.entry_table.setColumnWidth(5, 800)


    def toggleWordWrap(self):

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
        self.request_headers_tab_text.setPlainText('')
        self.request_body_tab_text.setPlainText('')
        self.request_query_tab_text.setPlainText('')
        self.request_cookie_tab_text.setPlainText('')
        self.response_headers_tab_text.setPlainText('')
        self.response_body_tab_text.setPlainText('')
        self.response_cookie_tab_text.setPlainText('')

    
    def searchEntries(self):

        # remove any previous search highlights
        self.clearSearch()

        if self.case_mode == 1:
            search_string = str(self.searchbox.text()).lower()
        else:
            search_string = str(self.searchbox.text())

        # if search string is blank clear out the ordered list of highligted rows
        if search_string == '':
            self.matched_ordered = []
            return()

        column_count = self.entry_table.columnCount()
        row_count = self.entry_table.rowCount()

        matched_items = []

        # look for tabs which contain the search string, grab the request UID
        # and find the UID in the table to get the QTableWidgetItem object

        for key, value in self.request_headers_dict.items():
            if self.case_mode == 1:
                if search_string in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
        
        for key, value in self.request_body_dict.items():
            if self.case_mode == 1:
                if search_string in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
        
        for key, value in self.request_cookies_dict.items():
            if self.case_mode == 1:
                if search_string in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))

        for key, value in self.request_queries_dict.items():
            if self.case_mode == 1:
                if search_string in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
        
        for key, value in self.response_headers_dict.items():
            if self.case_mode == 1:
                if search_string in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
        
        for key, value in self.response_body_dict.items():
            if self.case_mode == 1:
                if search_string in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
        
        for key, value in self.response_cookies_dict.items():
            if self.case_mode == 1:
                if search_string in str(value).lower():
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))
            else:
                if search_string in str(value):
                    matched_items.append(self.entry_table.findItems(key, Qt.MatchContains))

        # look for any entry table rows which contain the search string and 
        # get the QTableWidgetItem object
        matched_items.append(self.entry_table.findItems(search_string, Qt.MatchContains))

        # flatten the list of list
        matched_items = [item for sublist in matched_items for item in sublist]

        matched_rows = []

        # get the table row for each QTableWidgetItem object
        if len(matched_items) > 0:
            for item in matched_items:
                matched_rows.append(self.entry_table.row(item))
        # no matches
        else:
            self.status_bar.showMessage('No matches found')
            self.clearSearch()
            self.matched_ordered = []
            return()

        matched_rows = list(set(matched_rows))

        # highlight each cell of each table row where a match was found
        for row in matched_rows:
            for column in range(column_count):
                item = self.entry_table.item(row, column)
                item.setBackground(QColor(255, 255, 128))

        # get an ordered list of all matched rows
        self.matched_ordered = []
        for row in range(row_count):
            item = self.entry_table.item(row, 1)
            if item.background().color().blue() == 128:
                self.matched_ordered.append(row)

        if self.search_mode == 0:
            for row in range(row_count):
                if row not in matched_rows:
                    self.entry_table.setRowHidden(row, True)

        # activate the first row
        self.entry_table.setCurrentCell(self.matched_ordered[0], 1)
        self.status_bar.showMessage('Search Complete : {} Matches'.format(len(matched_rows)))


    def clearSearch(self):
        column_count = self.entry_table.columnCount()
        row_count = self.entry_table.rowCount()

        for row in range(row_count):
            # unhide
            self.entry_table.setRowHidden(row, False)
            # remove highlight
            for column in range(column_count):
                item = self.entry_table.item(row, column)
                item.setBackground(QColor(255, 255, 255))


    def previousMatch(self):
        
        # do nothing if there is there is no matches in the list or if
        # the list hasn't even been initalised (no HAR loaded)
        try:
            if self.matched_ordered == []:
                return()
        except AttributeError:
            return()

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

        # do nothing if there is there is no matches in the list or if
        # the list hasn't even been initalised (no HAR loaded)
        try:
            if self.matched_ordered == []:
                return()
        except AttributeError:
            return()

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

        # set current index for stepping through results
        self.current_index = 0

        # clear previous searches
        self.clearSearchRequest()

        find_flags = QTextDocument.FindFlags()
        
        # check for case sensitive matching mode
        if self.case_mode == 0:
            find_flags = QTextDocument.FindCaseSensitively
            
        # search string
        search_string = str(self.request_searchbox.text())

        if search_string == '':
            self.clearSearchRequest()
            return()

        # get active request tab
        active_tab = self.request_tabs.currentIndex()

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.request_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.request_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.request_query_tab_text
        elif active_tab == 3:
            active_qtextedit = self.request_cookie_tab_text            

        highlight_style = QTextCharFormat()
        highlight_style.setBackground(QBrush(QColor(255, 255, 128)))

        self.cursor_locations = []

        # move cursor to the start of the QTextEdit box
        active_qtextedit.moveCursor(QTextCursor.Start)

        while True:
            matches = active_qtextedit.find(search_string, find_flags)
            if matches:
                qc = active_qtextedit.textCursor()
                if qc.hasSelection():
                    self.cursor_locations.append(qc)
                    qc.mergeCharFormat(highlight_style)
            else:
                break

        self.status_bar.showMessage('Search Complete. Found {} Matches'.format(len(self.cursor_locations)))
    
    
    def nextMatchRequest(self):

        active_tab = self.request_tabs.currentIndex()

        print('test')

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.request_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.request_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.request_query_tab_text
        elif active_tab == 3:
            active_qtextedit = self.request_cookie_tab_text 

        if len(self.cursor_locations) > 0:
            active_qtextedit.setTextCursor(self.cursor_locations[self.current_index])
            if len(self.cursor_locations) - 1 == self.current_index:
                self.current_index = 0
            else:
                self.current_index += 1

    
    def clearSearchRequest(self):

        # get active request tab
        active_tab = self.request_tabs.currentIndex()

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.request_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.request_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.request_query_tab_text
        elif active_tab == 3:
            active_qtextedit = self.request_cookie_tab_text

        highlight_style = QTextCharFormat()
        highlight_style.setBackground(QBrush(QColor(255, 255, 255)))

        old_cursor = active_qtextedit.textCursor()
        active_qtextedit.selectAll()
        cursor = active_qtextedit.textCursor()
        cursor.mergeCharFormat(highlight_style)

        # reset the cursor
        active_qtextedit.moveCursor(QTextCursor.Start)
        
        # clear old cursor locations
        self.cursor_locations = []
        self.status_bar.clearMessage()
        

    def searchResponse(self):
        # set current index for stepping through results
        self.current_index = 0

        # clear previous searches
        self.clearSearchResponse()

        find_flags = QTextDocument.FindFlags()
        
        # check for case sensitive matching mode
        if self.case_mode == 0:
            find_flags = QTextDocument.FindCaseSensitively
            
        # search string
        search_string = str(self.response_searchbox.text())

        if search_string == '':
            self.clearSearchResponse()
            return()

        # get active request tab
        active_tab = self.response_tabs.currentIndex()

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.response_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.response_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.response_cookie_tab_text      

        highlight_style = QTextCharFormat()
        highlight_style.setBackground(QBrush(QColor(255, 255, 128)))

        self.cursor_locations = []

        # move cursor to the start of the QTextEdit box
        active_qtextedit.moveCursor(QTextCursor.Start)

        while True:
            matches = active_qtextedit.find(search_string, find_flags)
            if matches:
                qc = active_qtextedit.textCursor()
                if qc.hasSelection():
                    self.cursor_locations.append(qc)
                    qc.mergeCharFormat(highlight_style)
            else:
                break

        self.status_bar.showMessage('Search Complete. Found {} Matches'.format(len(self.cursor_locations)))
        

    def nextMatchResponse(self):

        active_tab = self.response_tabs.currentIndex()

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.response_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.response_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.response_cookie_tab_text

        if len(self.cursor_locations) > 0:
            active_qtextedit.setTextCursor(self.cursor_locations[self.current_index])
            if len(self.cursor_locations) - 1 == self.current_index:
                self.current_index = 0
            else:
                self.current_index += 1


    def clearSearchResponse(self):

        # get active request tab
        active_tab = self.response_tabs.currentIndex()

        # get active QTextEdit object
        if active_tab == 0:
            active_qtextedit = self.response_headers_tab_text
        elif active_tab == 1:
            active_qtextedit = self.response_body_tab_text
        elif active_tab == 2:
            active_qtextedit = self.response_cookie_tab_text

        highlight_style = QTextCharFormat()
        highlight_style.setBackground(QBrush(QColor(255, 255, 255)))

        old_cursor = active_qtextedit.textCursor()
        active_qtextedit.selectAll()
        cursor = active_qtextedit.textCursor()
        cursor.mergeCharFormat(highlight_style)

        # reset the cursor
        active_qtextedit.moveCursor(QTextCursor.Start)
        
        # clear old cursor locations
        self.cursor_locations = []
        self.status_bar.clearMessage()


class TableWidgetItem(QTableWidgetItem):
    def __init__(self, text, sortKey):
        QTableWidgetItem.__init__(self, text, QTableWidgetItem.UserType)
        self.sortKey = sortKey

    def __lt__(self, other):
        try:
            return self.sortKey < other.sortKey
        except TypeError:
            return -1


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 10))
    app.setStyle("Fusion")
    main_harshark = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()