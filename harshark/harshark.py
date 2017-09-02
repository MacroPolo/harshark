import ast
import json
import pprint
import random
import sqlite3
import string
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAbstractScrollArea
from PyQt5.QtWidgets import QHeaderView

class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # ---------------------------------------------------------
        # MENUBAR
        # ---------------------------------------------------------

        # create a menu bar
        menubar = self.menuBar()
        # add menus
        file_menu = menubar.addMenu('&File')
        view_menu = menubar.addMenu('&View')
        options_menu = menubar.addMenu('&Options')

        # open 
        open_act = QAction(QIcon('..\images\open.png'), '&Open', self)
        open_act.setShortcut('Ctrl+O')
        open_act.setStatusTip('Open a HAR file')
        # @TODO Open file explorer
        file_menu.addAction(open_act)

        # open recent
        open_recent = QMenu('Open &Recent', self)
        file_menu.addMenu(open_recent)

        # @TODO Generate a list of recent files
        open_recent_act_1 = QAction('Recent item 1', self)
        open_recent_act_2 = QAction('Recent item 2', self)
        open_recent_act_3 = QAction('Recent item 3', self)
        open_recent.addAction(open_recent_act_1)
        open_recent.addAction(open_recent_act_2)
        open_recent.addAction(open_recent_act_3)

        # quit 
        exit_act = QAction(QIcon('..\images\exit.png'), '&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit Harshark')
        exit_act.triggered.connect(qApp.quit)
        file_menu.addAction(exit_act)

        # ---------------------------------------------------------
        # TOOLBAR
        # ---------------------------------------------------------
       
        # create a toolbar for searching
        self.toolbar_actions = self.addToolBar('Useful commands')
        self.toolbar_search = self.addToolBar('Search & Filter')
        self.toolbar_actions.setFloatable(False)
        self.toolbar_search.setFloatable(False)

        # search box
        searchbox = QLineEdit(self)
        searchbox_lbl = QLabel('Search Filter', self)
        searchbox_lbl.setMargin(5)
        searchbox.setPlaceholderText('Enter search query here to filter the request list')
        
        # delete button
        delete_act = QAction(QIcon('..\images\delete.png'), '&Delete', self)
        delete_act.setStatusTip('Delete the selected requests')
        delete_act.triggered.connect(self.deleteRow)

        self.toolbar_actions.addAction(delete_act)
        self.toolbar_search.addWidget(searchbox_lbl)
        self.toolbar_search.addWidget(searchbox)

        # ---------------------------------------------------------
        # REQUEST TABLE
        # ---------------------------------------------------------

        # table widget which contains all requests
        self.my_table = QTableWidget()
        self.my_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.my_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.my_table.setColumnCount(13)
        self.my_table.setHorizontalHeaderLabels([
                                        'id',
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
                                        ])
        self.my_table.hideColumn(0)
        self.my_table.resizeColumnsToContents() 
        self.my_table.setColumnWidth(1, 200)
        self.my_table.setColumnWidth(3, 100)
        self.my_table.setColumnWidth(5, 600)
        self.my_table.horizontalHeader().setStretchLastSection(True)
        # when row clicked, fetch the request/response 
        self.my_table.itemSelectionChanged.connect(self.selectRow)
    
        # ---------------------------------------------------------
        # REQUEST TAB
        # ---------------------------------------------------------

        request_tabs = QTabWidget()

        request_headers_tab = QWidget()
        request_body_tab = QWidget()
        request_query_tab = QWidget()
        request_cookie_tab = QWidget()
        request_raw_tab = QWidget()

        request_tabs.addTab(request_headers_tab, 'Request Headers')
        request_tabs.addTab(request_body_tab, 'Request Body')
        request_tabs.addTab(request_query_tab, 'Request Query Strings')
        request_tabs.addTab(request_cookie_tab, 'Request Cookies')

        self.request_headers_tab_text = QTextEdit(acceptRichText=False)
        self.request_body_tab_text = QTextEdit(acceptRichText=False)
        self.request_query_tab_text = QTextEdit(acceptRichText=False)
        self.request_cookie_tab_text = QTextEdit(acceptRichText=False)

        self.request_headers_tab_text.setReadOnly(False)
        self.request_body_tab_text.setReadOnly(False)
        self.request_body_tab_text.setReadOnly(False)
        self.request_query_tab_text.setReadOnly(False)
        self.request_cookie_tab_text.setReadOnly(False)     

        request_headers_tab_layout = QVBoxLayout()
        request_body_tab_layout = QVBoxLayout()
        request_query_tab_layout = QVBoxLayout()
        request_cookie_tab_layout = QVBoxLayout()
        request_raw_tab_layout = QVBoxLayout()

        request_headers_tab_layout.addWidget(self.request_headers_tab_text)
        request_headers_tab.setLayout(request_headers_tab_layout)
        request_body_tab_layout.addWidget(self.request_body_tab_text)
        request_body_tab.setLayout(request_body_tab_layout)
        request_query_tab_layout.addWidget(self.request_query_tab_text)
        request_query_tab.setLayout(request_query_tab_layout)
        request_cookie_tab_layout.addWidget(self.request_cookie_tab_text)
        request_cookie_tab.setLayout(request_cookie_tab_layout)

        # ---------------------------------------------------------
        # RESPONSE TAB
        # ---------------------------------------------------------
        
        response_tabs = QTabWidget()

        response_headers_tab = QWidget()
        response_body_tab = QWidget()
        response_cookie_tab = QWidget()
        response_raw_tab = QWidget()

        response_tabs.addTab(response_headers_tab, 'Response Headers')
        response_tabs.addTab(response_body_tab, 'Response Body')
        response_tabs.addTab(response_cookie_tab, 'Response Cookies')

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
        # WIDGET SPLITTER
        # ---------------------------------------------------------

        splitter_hor = QSplitter(Qt.Horizontal)
        splitter_hor.addWidget(request_tabs)
        splitter_hor.addWidget(response_tabs)

        splitter_ver = QSplitter(Qt.Vertical)
        splitter_ver.addWidget(self.my_table)
        splitter_ver.addWidget(splitter_hor)

        self.setCentralWidget(splitter_ver)

        # ---------------------------------------------------------
        # SHORTCUTS
        # ---------------------------------------------------------

        self.shortcut_del = QShortcut(QKeySequence("Delete"), self)
        self.shortcut_del.activated.connect(self.deleteRow)

        # ---------------------------------------------------------
        # MAIN
        # ---------------------------------------------------------
        
        # app resolution
        self.resize(1600, 900)
        # center on the desktop
        self.centerWidget()
        # app title
        self.setWindowTitle('Harshark | HTTP Archive (HAR) Viewer | v0.1')
        # app icon
        self.setWindowIcon(QIcon('..\images\logo2.png'))
        # parse the HAR file
        self.harParse('archive5.har')
        # HarParse(harfile='archive2.har')
        # display the app
        self.show()

    def centerWidget(self):
        """Center the widget on the desktop."""
        # get the rectangle geometry of the widget including the frame
        widget_rectangle = self.frameGeometry()
        # get the resolution and center point of the desktop
        desktop_center = QDesktopWidget().availableGeometry().center()
        # move the center of widget_rectangle to desktop_center
        widget_rectangle.moveCenter(desktop_center)
        # move the top left of the widget to the top left of widget_rectangle
        self.move(widget_rectangle.topLeft())

    def deleteRow(self):
        """delete the selected rows from the requests table when hitting the 
        'delete' key
        """
        all_selection_groups = self.my_table.selectedRanges()
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
                self.my_table.removeRow(j)
            # decrement, to move to next row selection group
            number_of_selection_groups -= 1


    def harParse(self, archive):
        # @TODO error handling
        with open(archive, encoding='utf-8') as har:    
            har = json.load(har)

        self.request_headers_dict = {}
        self.request_body_dict = {}
        self.request_cookies_dict = {}
        self.request_queries_dict = {}

        self.response_headers_dict = {}
        self.response_body_dict = {}
        self.response_cookies_dict = {}
        
        # populate the entries table
        for i, entry in enumerate(har['log']['entries']):
            id = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(5))
            
            row_data = []
            row_data.append(id)
            row_data.append(entry['startedDateTime'])
            row_data.append(entry['time'])
            try:
                row_data.append(entry['serverIPAddress'])
            except KeyError:
                row_data.append('')
            row_data.append(entry['request']['method'])
            row_data.append(entry['request']['url'])
            row_data.append(entry['response']['status'])
            row_data.append(entry['response']['httpVersion'])
            row_data.append(entry['response']['content']['mimeType'])
            row_data.append(entry['request']['headersSize'])
            row_data.append(entry['request']['bodySize'])
            row_data.append(entry['response']['headersSize'])
            row_data.append(entry['response']['bodySize'])
            
            # fill the requests dictionaries
            self.request_headers_dict[id] = entry['request']['headers']
            try:
                self.request_body_dict[id] = entry['request']['postData']
            except KeyError:
                self.request_body_dict[id] = ''
            self.request_cookies_dict[id] = entry['request']['cookies']
            self.request_queries_dict[id] = entry['request']['queryString']

            # fill the response dictionaries
            self.response_headers_dict[id] = entry['response']['headers']
            self.response_body_dict[id] = entry['response']['content']
            self.response_cookies_dict[id] = entry['response']['cookies']

            # populate the entries table
            self.my_table.insertRow(i)
            for j, item in enumerate(row_data):
                self.my_table.setItem(i, j, QTableWidgetItem(str(item)))
            

    def selectRow(self):
        # @TODO tidy of exception handling and factor out

        body_safelist = [
                'text/html;charset=UTF-8', 
                'application/javascript',
                'application/json;charset=utf-8',
                'application/json;charset=UTF-8'
        ]

        self.request_headers_tab_text.setPlainText('')
        self.request_body_tab_text.setPlainText('')
        self.request_query_tab_text.setPlainText('')
        self.request_cookie_tab_text.setPlainText('')
        
        self.response_headers_tab_text.setPlainText('')
        self.response_body_tab_text.setPlainText('')
        self.response_cookie_tab_text.setPlainText('')

        row_id = self.my_table.item(self.my_table.currentRow(), 0).text()
        
        request_headers = self.request_headers_dict[row_id]
        request_body = self.request_body_dict[row_id]
        request_cookies = self.request_cookies_dict[row_id]
        request_queries = self.request_queries_dict[row_id]
        
        response_headers = self.response_headers_dict[row_id]
        response_body = self.response_body_dict[row_id]
        response_cookies = self.response_cookies_dict[row_id]

        for item in request_headers:
            entry = '<b>{}</b>: {}'.format(item['name'], item['value'])
            self.request_headers_tab_text.append(str(entry))

        if request_body != '':
            if request_body['mimeType'] in body_safelist:
                try:
                    entry = request_body['text']
                    self.request_body_tab_text.insertPlainText(str(entry))
                except KeyError:
                    self.request_body_tab_text.insertPlainText('No request body found')
            else:
                self.request_body_tab_text.append('Binary Data')  
        
        for item in request_queries:
            entry = '<b>{}</b>: {}'.format(item['name'], item['value'])
            self.request_query_tab_text.append(str(entry))
        
        for item in request_cookies:
            entry = '<b>{}</b>: {}'.format(item['name'], item['value'])
            self.request_cookie_tab_text.append(str(entry))

        for item in response_headers:
            entry = '<b>{}</b>: {}'.format(item['name'], item['value'])
            self.response_headers_tab_text.append(str(entry))

        if response_body['mimeType'] in body_safelist:
            try:
                entry = response_body['text']
                self.response_body_tab_text.insertPlainText(str(entry))
            except KeyError:
                self.response_body_tab_text.insertPlainText('No response body found')
        else:
            self.response_body_tab_text.append('Binary Data')      
        
        # @TODO can we get detailed cookie info? expiry time, flags etc
        for item in response_cookies:
            entry = '<b>{}</b>: {}'.format(item['name'], item['value'])
            self.response_cookie_tab_text.append(str(entry))

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 10))
  
    main_harshark = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()