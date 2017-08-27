import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
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
        self.resize(800, 600)
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
        # MAIN SPLITTER
        # ---------------------------------------------------------

        # table widget which contains all requests
        self.my_table = QTableWidget()
        self.my_table.setRowCount(5)
        self.my_table.setColumnCount(10)
        self.my_table.setSelectionBehavior(QTableWidget.SelectRows)

        # @TODO These should be non-editable widgets
        text_edit_2 = QTextEdit()
        text_edit_2.setReadOnly(True)
        text_edit_3 = QTextEdit()
        text_edit_3.setReadOnly(True)

        splitter_hor = QSplitter(Qt.Horizontal)
        splitter_hor.addWidget(text_edit_2)
        splitter_hor.addWidget(text_edit_3)

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