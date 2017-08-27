import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
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
from PyQt5.QtGui import QKeySequence

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
        self.setWindowTitle('Harshark | HTTP Archive (HAR) Viewer')
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

        # open action
        open_act = QAction(QIcon('..\images\open.png'), '&Open', self)
        open_act.setShortcut('Ctrl+O')
        open_act.setStatusTip('Open a HAR file')
        # @TODO Open file explorer
        file_menu.addAction(open_act)

        # quit action
        exit_act = QAction(QIcon('..\images\exit.png'), '&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.setStatusTip('Exit Harshark')
        exit_act.triggered.connect(qApp.quit)
        file_menu.addAction(exit_act)

        # ---------------------------------------------------------
        # TOOLBAR
        # ---------------------------------------------------------
       
        # create a toolbar
        self.toolbar = self.addToolBar('Search & Filter')

        # search box
        searchbox = QLineEdit(self)
        searchbox.setPlaceholderText('Enter search query here to filter the request list')
        searchbox_lbl = QLabel('Search Filter', self)

        # delete button
        delete_act = QAction(QIcon('..\images\delete.png'), '&Delete', self)
        delete_act.setShortcut('Delete')
        delete_act.setStatusTip('Delete the selected requests')
        delete_act.triggered.connect(self.delete_row)

        self.toolbar.addAction(delete_act)
        self.toolbar.addWidget(searchbox_lbl)
        self.toolbar.addWidget(searchbox)

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

def main():
    app = QApplication(sys.argv)
    # app.setFont(QFont('Segoe UI', 10))
    main_harshark = MainApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()