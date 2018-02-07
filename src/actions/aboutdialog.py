import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QWidget


class AboutDialog(QDialog):

    LICENSE_TEXT = """MIT License

Copyright (c) 2018 Mark Riddell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    INFO_TEXT = """Harshark: A simple offline HAR viewer.

Software description.

---------------------------------------------------------------------
Release 2.0.0 (dd-mmmm-yyyy)
---------------------------------------------------------------------
NEW FEATURES:
* Foo
* Bar

BUG FIXES:
* Foo
* Bar

NOTES:
* Foo Bar
"""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.initWidget()

    def initWidget(self):
        button_ok = QPushButton('OK', self)
        button_ok.clicked.connect(self.okPressed)

        about_tabs = QTabWidget()
        info_tab = QWidget()
        license_tab = QWidget()

        about_tabs.addTab(info_tab, 'Information')
        about_tabs.addTab(license_tab, 'License')

        info_tab_layout = QVBoxLayout()
        license_tab_layout = QVBoxLayout()

        info_tab_text = QPlainTextEdit(readOnly=True)
        license_tab_text = QPlainTextEdit(readOnly=True)

        info_tab_layout.addWidget(info_tab_text)
        info_tab.setLayout(info_tab_layout)

        license_tab_layout.addWidget(license_tab_text)
        license_tab.setLayout(license_tab_layout)

        info_tab_text.setPlainText(AboutDialog.INFO_TEXT)
        license_tab_text.setPlainText(AboutDialog.LICENSE_TEXT)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(about_tabs)
        main_layout.addWidget(button_ok)

        self.setLayout(main_layout)
        self.setWindowTitle("About Harshark")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(700 , 400)
        #self.setWindowIcon(self.app.column_select_icon)
        self.setStyleSheet("""
            QPlainTextEdit {
                    font-family: "Consolas";
                    font-size: 10pt;
                }
        """)
        self.exec_()

    def okPressed(self):
        self.close()
