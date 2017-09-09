import json
import random
import string
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QTextOption
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFontDialog
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QAbstractScrollArea
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QSpinBox


class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
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
        delete_act = QAction(QIcon('..\images\delete.png'), '&Delete', self)
        delete_act.setStatusTip('Delete the selected requests')
        delete_act.setShortcut('Delete')
        delete_act.triggered.connect(self.deleteRow)

        #expand
        expand_act = QAction(QIcon('..\images\expand.png'), 'Expand', self)
        expand_act.setStatusTip('Show full response body content')
        expand_act.setShortcut('Ctrl+X')
        expand_act.triggered.connect(self.expandBody)

        #font choice
        font_act = QAction(QIcon('..\images\\font.png'), 'Change &Font...', self)
        font_act.setStatusTip('Change the font used to display request/response information')        
        font_act.triggered.connect(self.changeFont)

        #resize columns to fit
        resize_col_act = QAction(QIcon('..\images\\resize.png'), '&Resize Columns', self)
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
        view_menu = menu_bar.addMenu('&View')
        options_menu = menu_bar.addMenu('&Options')

        file_menu.addAction(open_act)
        file_menu.addAction(exit_act)

        options_menu.addAction(font_act)

        view_menu.addAction(resize_col_act)
        view_menu.addAction(wordwrap_act)
        
        
        # ---------------------------------------------------------
        # TOOLBARS
        # ---------------------------------------------------------
        
        self.toolbar_actions = self.addToolBar('Useful commands')
        self.toolbar_search = self.addToolBar('Search & Filter')

        self.toolbar_search.setFloatable(False)
        self.toolbar_actions.setFloatable(False)

        self.toolbar_actions.addAction(open_act)
        self.toolbar_actions.addAction(delete_act)
        self.toolbar_actions.addAction(expand_act)
        self.toolbar_actions.addAction(resize_col_act)
        
        searchbox = QLineEdit(self)
        searchbox_lbl = QLabel('Search Filter', self)
        searchbox_lbl.setMargin(5)
        searchbox.setPlaceholderText('Enter search query here to highlight matches')
        self.toolbar_search.addWidget(searchbox_lbl)
        self.toolbar_search.addWidget(searchbox)
        
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
        self.entry_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.entry_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entry_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entry_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.entry_table.setColumnCount(len(header_labels))
        self.entry_table.setHorizontalHeaderLabels(header_labels)
        self.entry_table.hideColumn(0)
        # when row clicked, fetch the request/response
        self.entry_table.itemSelectionChanged.connect(self.selectRow)

        # ---------------------------------------------------------
        # REQUESTS TAB
        # ---------------------------------------------------------

        request_tabs = QTabWidget()

        request_headers_tab = QWidget()
        request_body_tab = QWidget()
        request_query_tab = QWidget()
        request_cookie_tab = QWidget()

        request_tabs.addTab(request_headers_tab, 'Headers')
        request_tabs.addTab(request_body_tab, 'Body')
        request_tabs.addTab(request_query_tab, 'Query Strings')
        request_tabs.addTab(request_cookie_tab, 'Cookies')

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
        
        response_tabs = QTabWidget()

        response_headers_tab = QWidget()
        response_body_tab = QWidget()
        response_cookie_tab = QWidget()

        response_tabs.addTab(response_headers_tab, 'Headers')
        response_tabs.addTab(response_body_tab, 'Body')
        response_tabs.addTab(response_cookie_tab, 'Cookies')

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

        request_vbox = QVBoxLayout()
        response_vbox = QVBoxLayout()

        request_searchbox = QLineEdit(self)
        response_searchbox = QLineEdit(self)        
        request_searchbox.setPlaceholderText('Enter search query here to highlight matches')
        response_searchbox.setPlaceholderText('Enter search query here to highlight matches')

        request_vbox.addWidget(request_tabs)
        request_vbox.addWidget(request_searchbox)

        response_vbox.addWidget(response_tabs)
        response_vbox.addWidget(response_searchbox)        

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
        self.setWindowTitle('Harshark | HTTP Archive (HAR) Viewer | v0.2')
        # app icon
        self.setWindowIcon(QIcon('..\images\logo2.png'))
        # display the app
        self.show()

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

    def harParse(self):

        # initalise dictionaries used to store entry details
        self.request_headers_dict = {}
        self.request_body_dict = {}
        self.request_cookies_dict = {}
        self.request_queries_dict = {}
        self.response_headers_dict = {}
        self.response_body_dict = {}
        self.response_cookies_dict = {}

        # columns which should be sorted as numbers rather than strings
        numeric_columns = [2, 3, 6, 9, 10, 11, 12]

        # HAR file none types
        none_types = [None, '']

        # remove any previous rows which may exist from a previous file
        self.entry_table.setRowCount(0)

        # turn off sorting
        self.entry_table.setSortingEnabled(False)
        
        # initialise progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumWidth(300)
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
                if entry['startedDateTime'] in none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['startedDateTime'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['time'] in none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['time'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['serverIPAddress'] in none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['serverIPAddress'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['request']['method'] in none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['request']['method'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['request']['url'] in none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['request']['url'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['response']['status'] in none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['response']['status'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['response']['httpVersion'] in none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['response']['httpVersion'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['response']['content']['mimeType'] in none_types:
                    row_data.append('-')
                else:
                    row_data.append(entry['response']['content']['mimeType'])
            except KeyError:
                row_data.append('-')
            
            try:
                if entry['request']['headersSize'] in none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['request']['headersSize'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['request']['bodySize'] in none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['request']['bodySize'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['response']['headersSize'] in none_types:
                    row_data.append(-1)
                else:
                    row_data.append(entry['response']['headersSize'])
            except KeyError:
                row_data.append(-1)
            
            try:
                if entry['response']['bodySize'] in none_types:
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
                    item = TableWidgetItem(str(item), item)
                    self.entry_table.setItem(i, j, item)
                # otherwise business as usual
                else:
                    self.entry_table.setItem(i, j, QTableWidgetItem(str(item)))
            
            # fill the requests dictionaries
            try:
                self.request_headers_dict[id] = entry['request']['headers']
            except KeyError:
                self.request_headers_dict[id] = ' No request headers found'
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
                self.request_queries_dict[id] =''

            # fill the response dictionaries
            try:
                self.response_headers_dict[id] = entry['response']['headers']
            except KeyError:
                self.response_headers_dict[id] = 'No response headers found'
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
        self.status_bar.showMessage('HAR imported sucessfully')

        # turn on sorting
        self.entry_table.setSortingEnabled(True)

        # resize columns to fit
        self.resizeColumns()

        self.entry_table.setFont(QFont('Segoe UI', 10))

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
        
    def selectRow(self):

        truncate_size = 2000

        body_safelist = [
                'text', 
                'html',
                'css',
                'json',
                'javascript',
                'js',
                'xml'
        ]

        cookie_list = []

        self.request_headers_tab_text.setPlainText('')
        self.request_body_tab_text.setPlainText('')
        self.request_query_tab_text.setPlainText('')
        self.request_cookie_tab_text.setPlainText('')
        self.response_headers_tab_text.setPlainText('')
        self.response_body_tab_text.setPlainText('')
        self.response_cookie_tab_text.setPlainText('')

        # all rows have been deleted
        if self.entry_table.currentRow() == -1:
            return

        row_id = self.entry_table.item(self.entry_table.currentRow(), 0).text()
        
        request_headers = self.request_headers_dict[row_id]
        request_body = self.request_body_dict[row_id]
        request_cookies = self.request_cookies_dict[row_id]
        request_queries = self.request_queries_dict[row_id]
        response_headers = self.response_headers_dict[row_id]
        response_body = self.response_body_dict[row_id]
        response_cookies = self.response_cookies_dict[row_id]

        for item in request_headers:
            entry = '<p><b>{}</b><br>{}'.format(item['name'], item['value'])
            self.request_headers_tab_text.append(str(entry))

        if request_body != '':
            if any(mime in request_body['mimeType'] for mime in body_safelist):
                try:
                    entry = request_body['text']
                    self.request_body_tab_text.insertPlainText(str(entry))
                except KeyError:
                    self.request_body_tab_text.insertPlainText('No request body found')
            elif request_body['mimeType'] == '':
                self.request_body_tab_text.insertPlainText('')
            else:
                self.request_body_tab_text.insertPlainText('Non ASCII request')  
        else:
            self.request_body_tab_text.insertPlainText('')  
        
        for item in request_queries:
            entry = '<p>     <b>{}</b><br>{}'.format(item['name'], item['value'])
            self.request_query_tab_text.append(str(entry))
        
        for item in request_cookies:
            entry = '<p>     <b>{}</b><br>{}'.format(item['name'], item['value'])
            self.request_cookie_tab_text.append(str(entry))

        # parse response headers
        for item in response_headers:

            # display response headers
            entry = '<b>{}</b><br>{}<br>'.format(item['name'], item['value'])
            self.response_headers_tab_text.append(str(entry))

            # parse 'set-cookie header in response header if we don't have them 
            # in nice HAR format
            if not response_cookies:
                if item['name'] == 'Set-Cookie' or item['name'] == 'set-cookie':
                    cookie_header = item['value'].split('\n')
                    for cookie in cookie_header:
                        this_cookie = cookie.split(';')
                        for each in this_cookie:
                            self.response_cookie_tab_text.append(each.strip())
                        self.response_cookie_tab_text.append('')

        # parse response body

        if response_body != '':
            if any(mime in response_body['mimeType'] for mime in body_safelist):
                try:
                    entry = response_body['text'][:truncate_size]
                    if len(entry) == truncate_size:
                        entry = '---BODY TRUNCATED--- (Ctrl+X to expand)\n\n' + str(entry)
                    self.response_body_tab_text.insertPlainText(entry)
                except KeyError:
                    self.response_body_tab_text.insertPlainText('No response body found')
            else:
                self.response_body_tab_text.insertPlainText('Non ASCII response')
        else:
            self.response_body_tab_text.insertPlainText('No response body found')
    
        # parse response cookies

        if response_cookies:
            for item in response_cookies:
                
                cookie = {'name':'',
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
                entry = '''<b>Name</b>: {}<br>
                            <b>Value</b>: {}<br>
                            <b>Path</b>: {}<br>
                            <b>Domain</b>: {}<br>
                            <b>Expires</b>: {}<br>
                            <b>httpOnly</b>: {}<br>
                            <b>Secure</b>: {}<br>'''.format(
                                cookie['name'], cookie['value'], cookie['path'],
                                cookie['domain'], cookie['expires'], cookie['httpOnly'],
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
        body_text = self.response_body_tab_text.toPlainText()

        # show full response body if we know it's been truncated
        if '---BODY TRUNCATED---' in body_text:
            response_body = self.response_body_dict[row_id]
            entry = str(response_body['text'])
            self.response_body_tab_text.setPlainText('')
            self.response_body_tab_text.insertPlainText(entry)
        
        return

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