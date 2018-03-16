from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor

from actions.generic import clearTabSearch

class EntrySelector():
    def __init__(self, app):
        self.app = app
        self.entry_data = None
        self.main()

    def main(self):
        self._collectData()
        self._prepareTabs()
        self._populateRequestHeaders()
        self._populateRequestParams()
        self._populateRequestCookies()
        self._populateRequestBody()
        self._populateRequestSaml()
        self._populateResponseHeaders()
        self._populateResponseCookies()
        self._populateResponseBody()

    def _collectData(self):
        row_id = self.app.entries_table.item(self.app.entries_table.currentRow(), 0).text()
        self.entry_data = self.app.har_parsed[row_id]

    def _prepareTabs(self):
        """Clear the textboxes and remove any highlighting."""
        for textedit in self.app.request_textedits + self.app.response_textedits:
            textedit.setPlainText('')
        clearTabSearch(self.app, tab_group='all')

    def _populateRequestHeaders(self):
        request_headers = self.entry_data['request_headers']
        request_method = self.entry_data['request_method'].upper()
        request_url = self.entry_data['request_url']
        request_version = self.entry_data['request_httpVersion'].upper()
        request_summary = '{} {} {}\n'.format(request_method, request_url, request_version)
        self.app.request_headers_tab_text.append(request_summary)

        sort_headers = self.app.config.getConfig('sort-headers')
        if sort_headers:
            request_headers = sorted(request_headers, key=lambda name: name['name'])
            
        for header in request_headers:
            entry = '<b>{}</b>: {}'.format(header.get('name'), header.get('value'))
            self.app.request_headers_tab_text.append(entry)

        self.app.request_headers_tab_text.moveCursor(QTextCursor.Start)

    def _populateRequestParams(self):
        for param in self.entry_data['request_queryString']:
            # query string parameters may have names only without any values
            if not param.get('value'):
                entry = '{}'.format(param.get('name'))
            else:
                entry = '<b>{}</b>: {}'.format(param.get('name'), param.get('value'))
            self.app.request_query_tab_text.append(entry)

        self._toggleTabVisibility(self.app.request_tabs, self.app.request_query_tab_text, 1)
        self.app.request_query_tab_text.moveCursor(QTextCursor.Start)

    def _populateRequestCookies(self):
        for cookie in self.entry_data['request_cookies']:
            # self-constructed cookie objects (strings)
            try:
                self.app.request_cookie_tab_text.append(cookie)
            # cookie object from HAR (dicts)
            except TypeError:
                for param in cookie:
                    entry = '<b>{}</b>: {}'.format(param, cookie[param])
                    self.app.request_cookie_tab_text.append(entry)
                self.app.request_cookie_tab_text.append('')

        self._toggleTabVisibility(self.app.request_tabs, self.app.request_cookie_tab_text, 2)
        self.app.request_cookie_tab_text.moveCursor(QTextCursor.Start)

    def _populateRequestBody(self):
        post_text = self.entry_data['request_postData_text']
        post_params = self.entry_data['request_postData_params']

        if post_text:
            # truncate large post bodies by default
            truncate_length = self.app.config.getConfig('truncate-character-count')
            if len(post_text) > truncate_length:
                self.app.request_expand_button.show()
                self.app.request_body_tab_text.appendPlainText(post_text[:truncate_length])
                self.app.request_body_tab_text.appendPlainText('. . .')
            else:
                self.app.request_expand_button.hide()
                self.app.request_body_tab_text.appendPlainText(post_text)

        elif post_params:
            for param in post_params:
                for k, v in param.items():
                    entry = '{}: {}'.format(k, v)
                    self.app.request_body_tab_text.appendPlainText(entry)
                self.app.request_body_tab_text.appendPlainText('')
            self.app.request_expand_button.hide()

        self.app.request_body_tab_text.moveCursor(QTextCursor.Start)
        self._toggleTabVisibility(self.app.request_tabs, self.app.request_body_tab_text, 3)
    
    def _populateRequestSaml(self):
        saml_request = self.entry_data['saml_request']
        saml_response = self.entry_data['saml_response']
        
        if saml_request:
            self.app.request_saml_tab_text.appendPlainText(saml_request)
        else:
            self.app.request_saml_tab_text.appendPlainText(saml_response)
        
        self.app.request_saml_tab_text.moveCursor(QTextCursor.Start)
        self._toggleTabVisibility(self.app.request_tabs, self.app.request_saml_tab_text, 4)

    def _populateResponseHeaders(self):
        response_headers = self.entry_data['response_headers']
        response_version = self.entry_data['response_httpVersion'].upper()  
        response_status_code = self.entry_data['response_status']
        response_status_text = self.entry_data['response_statusText']
        response_summary = '{} {} {}\n'.format(response_version, response_status_code, response_status_text)
        self.app.response_headers_tab_text.append(response_summary)

        # sort response headers by name
        sort_headers = self.app.config.getConfig('sort-headers')
        if sort_headers:
            response_headers = sorted(response_headers, key=lambda name: name['name'])

        for header in response_headers:
            entry = '<b>{}</b>: {}'.format(header.get('name'), header.get('value'))
            self.app.response_headers_tab_text.append(entry)

        self.app.response_headers_tab_text.moveCursor(QTextCursor.Start)

    def _populateResponseCookies(self):
        for cookie in self.entry_data['response_cookies']:
            # self-constructed cookie objects (strings)
            try:
                self.app.response_cookie_tab_text.append(cookie)
            # cookie object from HAR (dicts)
            except TypeError:
                for param in cookie:
                    entry = '<b>{}</b>: {}'.format(param, cookie[param])
                    self.app.response_cookie_tab_text.append(entry)
                self.app.response_cookie_tab_text.append('')

        self._toggleTabVisibility(self.app.response_tabs, self.app.response_cookie_tab_text, 1)
        self.app.response_cookie_tab_text.moveCursor(QTextCursor.Start)

    def _populateResponseBody(self):
        response_content = self.entry_data['response_content_text']
        # truncate large response content by default
        truncate_length = self.app.config.getConfig('truncate-character-count')
        if len(response_content) > truncate_length:
            self.app.response_expand_button.show()
            self.app.response_body_tab_text.appendPlainText(response_content[:truncate_length])
            self.app.response_body_tab_text.appendPlainText('. . .')
        else:
            self.app.response_expand_button.hide()
            self.app.response_body_tab_text.appendPlainText(response_content)

        self.app.response_body_tab_text.moveCursor(QTextCursor.Start)
        self._toggleTabVisibility(self.app.response_tabs, self.app.response_body_tab_text, 2)

    @staticmethod
    def _toggleTabVisibility(tab, text_edit, position):
        """If the tab contains no data, disable it, otherwise enable it."""
        if not text_edit.toPlainText():
            tab.setTabEnabled(position, False)
        else:
            tab.setTabEnabled(position, True)
