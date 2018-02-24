from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QTreeWidgetItemIterator


from actions.generic import toggleColumnVisibility

class ColumnSelectDialog(QDialog):
    """Widget to toggle column visibility in the entries table."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.column_config = app.config.getConfig('table_columns')
        self.header_categories = ['General', 'Request', 'Response', 'Timing']
        self.initWidget()

    def initWidget(self):

        with open(self.app.stylesheet_path, 'r') as f:
            self.setStyleSheet(f.read())

        self.selector_tree = QTreeWidget()
        self.selector_tree.setHeaderHidden(True)

        self.button_ok = QPushButton('OK', self)
        self.button_cancel = QPushButton('Cancel', self)
        self.button_ok.clicked.connect(self.okPressed)
        self.button_cancel.clicked.connect(self.cancelPressed)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.selector_tree)
        main_layout.addWidget(self.button_ok)
        main_layout.addWidget(self.button_cancel)

        self.setLayout(main_layout)
        self.resize(320, 620)
        self.setMaximumWidth(320)
        self.setMaximumHeight(620)
        self.setWindowTitle("Choose Columns to Display")
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(self.app.column_select_icon)
        self.populateTree()
        self.exec_()

    def populateTree(self):
        for category in self.header_categories:

            # add header categories
            parent = QTreeWidgetItem(self.selector_tree)
            parent.setText(0, category)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            parent.setExpanded(True)

            # add column headers as children to each category
            for column, attributes in self.column_config.items():
                # prevent request ID from being selectable
                if attributes.get('name') != 'Request ID':
                    if attributes.get('category') == category:
                        child = QTreeWidgetItem(parent)
                        child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                        child.setText(0, attributes.get('name'))
                        if attributes.get('visible'):
                            child.setCheckState(0, Qt.Checked)
                        else:
                            child.setCheckState(0, Qt.Unchecked)

    def okPressed(self):
        tree_iterator = QTreeWidgetItemIterator(self.selector_tree)

        while tree_iterator.value():
            item = tree_iterator.value()
            column_text = item.text(0)
            column_visible = item.checkState(0)

            if column_visible == 0:
                column_visible = False
            if column_visible == 2:
                column_visible = True

            # ignore header categories
            if column_text not in self.header_categories:
                for column, attributes in self.column_config.items():
                    if column_text == attributes.get('name'):
                        attributes['visible'] = column_visible

            tree_iterator += 1

        self.app.config.setConfig('table_columns', self.column_config)
        toggleColumnVisibility(self.app)
        self.close()

    def cancelPressed(self):
        self.close()
