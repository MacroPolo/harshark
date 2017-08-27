import sys
import json
import sqlite3
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QKeySequence
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
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QMenu


class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # ---------------------------------------------------------
        # MAIN SETTINGS
        # ---------------------------------------------------------

        # main resolution
        self.resize(1600, 900)
        # center on the desktop
        self.center_widget()
        # app title
        self.setWindowTitle('Harshark | HTTP Archive (HAR) Viewer | v0.1')
        # app icon
        self.setWindowIcon(QIcon('..\images\logo2.png'))

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
        delete_act.triggered.connect(self.delete_row)

        self.toolbar_actions.addAction(delete_act)
        self.toolbar_search.addWidget(searchbox_lbl)
        self.toolbar_search.addWidget(searchbox)

        # ---------------------------------------------------------
        # REQUEST TABLE
        # ---------------------------------------------------------

        # table widget which contains all requests
        self.my_table = QTableWidget()
        self.my_table.setRowCount(5)
        self.my_table.setColumnCount(10)
        self.my_table.setSelectionBehavior(QTableWidget.SelectRows)

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
        request_tabs.addTab(request_raw_tab, 'Raw Request')

        request_headers_tab_text = QTextEdit()
        request_body_tab_text = QTextEdit()
        request_query_tab_text = QTextEdit()
        request_cookie_tab_text = QTextEdit()
        request_raw_tab_text = QTextEdit()

        request_headers_tab_text.setReadOnly(False)
        request_body_tab_text.setReadOnly(False)
        request_query_tab_text.setReadOnly(False)
        request_cookie_tab_text.setReadOnly(False)
        request_raw_tab_text.setReadOnly(False)        

        request_headers_tab_layout = QVBoxLayout()
        request_body_tab_layout = QVBoxLayout()
        request_query_tab_layout = QVBoxLayout()
        request_cookie_tab_layout = QVBoxLayout()
        request_raw_tab_layout = QVBoxLayout()

        request_headers_tab_layout.addWidget(request_headers_tab_text)
        request_headers_tab.setLayout(request_headers_tab_layout)
        request_body_tab_layout.addWidget(request_body_tab_text)
        request_body_tab.setLayout(request_body_tab_layout)
        request_query_tab_layout.addWidget(request_query_tab_text)
        request_query_tab.setLayout(request_query_tab_layout)
        request_cookie_tab_layout.addWidget(request_cookie_tab_text)
        request_cookie_tab.setLayout(request_cookie_tab_layout)
        request_raw_tab_layout.addWidget(request_raw_tab_text)
        request_raw_tab.setLayout(request_raw_tab_layout)

        # ---------------------------------------------------------
        # RESPONSE TAB
        # ---------------------------------------------------------
        
        response_tabs = QTabWidget()

        response_headers_tab = QWidget()
        response_body_tab = QWidget()
        response_query_tab = QWidget()
        response_cookie_tab = QWidget()
        response_raw_tab = QWidget()

        response_tabs.addTab(response_headers_tab, 'Response Headers')
        response_tabs.addTab(response_body_tab, 'Response Body')
        response_tabs.addTab(response_query_tab, 'Response Query Strings')
        response_tabs.addTab(response_cookie_tab, 'Response Cookies')
        response_tabs.addTab(response_raw_tab, 'Raw response')

        response_headers_tab_text = QTextEdit()
        response_body_tab_text = QTextEdit()
        response_query_tab_text = QTextEdit()
        response_cookie_tab_text = QTextEdit()
        response_raw_tab_text = QTextEdit()

        response_headers_tab_text.setReadOnly(False)
        response_body_tab_text.setReadOnly(False)
        response_query_tab_text.setReadOnly(False)
        response_cookie_tab_text.setReadOnly(False)
        response_raw_tab_text.setReadOnly(False)        

        response_headers_tab_layout = QVBoxLayout()
        response_body_tab_layout = QVBoxLayout()
        response_query_tab_layout = QVBoxLayout()
        response_cookie_tab_layout = QVBoxLayout()
        response_raw_tab_layout = QVBoxLayout()

        response_headers_tab_layout.addWidget(response_headers_tab_text)
        response_headers_tab.setLayout(response_headers_tab_layout)
        response_body_tab_layout.addWidget(response_body_tab_text)
        response_body_tab.setLayout(response_body_tab_layout)
        response_query_tab_layout.addWidget(response_query_tab_text)
        response_query_tab.setLayout(response_query_tab_layout)
        response_cookie_tab_layout.addWidget(response_cookie_tab_text)
        response_cookie_tab.setLayout(response_cookie_tab_layout)
        response_raw_tab_layout.addWidget(response_raw_tab_text)
        response_raw_tab.setLayout(response_raw_tab_layout)

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
        # KEYBOARD SHORTCUTS
        # ---------------------------------------------------------

        # Delete key to remove entries from the requests table
        self.shortcut = QShortcut(QKeySequence("Delete"), self)
        self.shortcut.activated.connect(self.delete_row)
        self.create_db()
        self.show()

    def center_widget(self):
        """Center the widget on the desktop."""
        # get the rectangle geometry of the widget including the frame
        widget_rectangle = self.frameGeometry()
        # get the resolution and center point of the desktop
        desktop_center = QDesktopWidget().availableGeometry().center()
        # move the center of widget_rectangle to desktop_center
        widget_rectangle.moveCenter(desktop_center)
        # move the top left of the widget to the top left of widget_rectangle
        self.move(widget_rectangle.topLeft())

    def delete_row(self):
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

    def create_db(self):
        conn = sqlite3.connect('har.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS requests
        (timestamp              DATETIME           NOT NULL,
        time                    TEXT,
        server_ip               TEXT,
        port                    TEXT,
        request_body_size       TEXT,
        request_method          TEXT,
        request_url             TEXT,
        request_http_version    TEXT,
        request_headers         TEXT,
        request_cookies         TEXT,
        request_query_string    TEXT,
        response_status         TEXT,
        response_status_text    TEXT,
        response_http_version   TEXT,
        response_headers        TEXT,
        response_cookies        TEXT,
        response_body           TEXT,
        response_redirect_url   TEXT,
        response_headers_size   TEXT,
        response_body_size      TEXT,
        timings_blocked         TEXT,
        timings_dns             TEXT,
        timings_connect         TEXT,
        timings_send            TEXT,
        timings_wait            TEXT,
        timings_receive         TEXT,
        timings_ssl             TEXT
        )''')

        my_dict = {
            'timestamp':'', 
            'time':'', 
            'server_ip':'', 
            'port':'', 
            'request_body_size':'', 
            'request_method':'', 
            'request_url':'', 
            'request_headers':'', 
            'request_cookies':'', 
            'request_query_string':'', 
            'response_status':'', 
            'response_status_text':'', 
            'response_http_version':'', 
            'response_headers':'', 
            'response_cookies':'', 
            'response_body':'', 
            'response_redirect_url':'', 
            'response_headers_size':'', 
            'response_body_size':'', 
            'timings_blocked':'', 
            'timings_dns':'', 
            'timings_connect':'', 
            'timings_send':'', 
            'timings_wait':'',
            'timings_receive':'',
            'timings_ssl':''
        }

        with open('archive.har') as har:    
            har = json.load(har)
        for entry in har['log']['entries']:
            try:
                my_dict['timestamp'] = entry['startedDateTime']
            except KeyError:
                pass
            try:
                my_dict['time'] = entry['time']
            except KeyError:
                pass
            try:
                my_dict['server_ip'] = entry['serverIPAddress']
            except KeyError:
                pass
            try:
                my_dict['port'] = entry['connection']
            except KeyError:
                pass
            try:                 
                my_dict['request_body_size'] = entry['request']['bodySize']
            except KeyError:
                pass

            c.execute("INSERT INTO requests \
                            VALUES (?, ?, ?, ?, ?)", 
                        (my_dict['timestamp'],
                        my_dict['time'],
                        my_dict['server_ip'],
                        my_dict['port'],
                        my_dict['request_body_size']
                        ))
        conn.commit()
        conn.close()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 10))
    main_harshark = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()