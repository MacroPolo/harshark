import math

from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextCursor

def resizeColumns(app):
    app.entries_table.resizeColumnsToContents()
    app.entries_table.setColumnWidth(6, 800)    # request URL
    app.entries_table.setColumnWidth(12, 800)   # redirect URL

def _statusCodeFloor(status_code):
    # 403 = 400
    return str(math.floor(int(status_code) / 100) * 100)

def decolourizeCells(app):
    row_count = app.entries_table.rowCount()

    colour_default_hex = app.config.getConfig('colour_scheme')['default']
    colour_default = QColor(colour_default_hex)

    for row in range(row_count):
        app.entries_table.item(row, 4).setBackground(QColor(colour_default)) # method
        app.entries_table.item(row, 5).setBackground(QColor(colour_default)) # protocol
        app.entries_table.item(row, 8).setBackground(QColor(colour_default)) # status code

def colourizeCells(app):
    row_count = app.entries_table.rowCount()
    method_colours = app.config.getConfig('colour_scheme')['method']
    protocol_colours = app.config.getConfig('colour_scheme')['protocol']
    status_code_colours = app.config.getConfig('colour_scheme')['status']

    for row in range(row_count):

        method_item = app.entries_table.item(row, 4)
        protocol_item = app.entries_table.item(row, 5)
        status_code_item = app.entries_table.item(row, 8)

        # request methods
        for method, colour in method_colours.items():
            if method == method_item.text().lower():
                method_item.setBackground(QColor(colour))

        # request protocol
        for protocol, colour in protocol_colours.items():
            if protocol == protocol_item.text().lower():
                protocol_item.setBackground(QColor(colour))

        # status codes
        for status_code, colour in status_code_colours.items():
            if _statusCodeFloor(status_code_item.text()) == status_code:
                status_code_item.setBackground(QColor(colour))

def toggleColumnVisibility(app):
    column_config = app.config.getConfig('table_columns')
    for k, v in column_config.items():
        if v.get('visible'):
            app.entries_table.showColumn(v.get('index'))
        else:
            app.entries_table.hideColumn(v.get('index'))

def clearEntriesSearch(app):
    column_count =  app.entries_table.columnCount()
    row_count =  app.entries_table.rowCount()

    colour_match_hex = app.config.getConfig('colour_scheme')['search_match']
    colour_default_hex = app.config.getConfig('colour_scheme')['default']
    colour_match = QColor(colour_match_hex).rgb()
    colour_default = QColor(colour_default_hex)

    for row in range(row_count):
        for column in range(column_count):
            cell_colour = app.entries_table.item(row, column).background().color().rgb()
            if cell_colour == colour_match:
                app.entries_table.item(row, column).setBackground(colour_default)

    app.next_match_entries.setEnabled(False)
    app.clear_match_entries.setEnabled(False)

    app.statusbar.clearMessage()

def clearTabSearch(app, tab_group='all'):
    colour_default_hex = app.config.getConfig('colour_scheme')['default']
    colour_default = QColor(colour_default_hex)

    eraser = QTextCharFormat()
    eraser.setBackground(QBrush(colour_default))

    if tab_group == 'request':
        tabs = app.request_textedits
        app.statusbar.clearMessage()
        app.clear_match_request_btn.setEnabled(False)
        app.next_match_request_btn.setEnabled(False)
    elif tab_group == 'response':
        tabs = app.response_textedits
        app.clear_match_response_btn.setEnabled(False)
        app.next_match_response_btn.setEnabled(False)
    else:
        tabs = app.request_textedits + app.response_textedits
        app.statusbar.clearMessage()
        app.clear_match_request_btn.setEnabled(False)
        app.next_match_request_btn.setEnabled(False)
        app.clear_match_response_btn.setEnabled(False)
        app.next_match_response_btn.setEnabled(False)

    for tab in tabs:
        tab.selectAll()
        cursor = tab.textCursor()
        cursor.mergeCharFormat(eraser)
        tab.moveCursor(QTextCursor.Start)

def expandBody(app, body_type):
    row_id = app.entries_table.item(app.entries_table.currentRow(), 0).text()
    entry_data = app.har_parsed[row_id]

    if body_type == 'request':
        post_body = entry_data['request_postData_text']
        app.request_expand_button.hide()
        app.request_body_tab_text.setPlainText('')
        app.request_body_tab_text.appendPlainText(post_body)
        app.request_body_tab_text.moveCursor(QTextCursor.Start)
    else:
        response_body = entry_data['response_content_text']
        app.response_expand_button.hide()
        app.response_body_tab_text.setPlainText('')
        app.response_body_tab_text.appendPlainText(response_body)
        app.response_body_tab_text.moveCursor(QTextCursor.Start)
