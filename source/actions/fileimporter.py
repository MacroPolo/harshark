import json
import random
import re
import string
import time

from base64 import b64decode
from zlib import decompress

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTableWidgetItem

from harshark_exceptions import HarImportException
from actions.generic import colourizeCells
from actions.generic import resizeColumns
from actions.generic import toggleColumnVisibility

class FileImporter():
    def __init__(self, app):
        self.app = app
        self.har_path = None
        self.har_raw = None
        self.import_start = None
        self.har_summary = {}
        self.har_parsed = {}
        self.main()

    def main(self):
        self._openFile()
        self._validateFile()
        self._parseFile()
        self._populateTable()
        self._finalise()

    def _openFile(self):
        """Open an explorer window to allow the user to select a HAR file to be
        imported. Store the absolute path reference to the selected file."""
        self.har_path = QFileDialog.getOpenFileName(self.app, 'Open HAR File')[0]
        if not self.har_path:
            raise HarImportException

    def _validateFile(self):
        """File validation. We need to ensure that the user has selected a
        valid JSON file conforming to the HAR 1.1/1.2 specification."""

        self.app.statusbar.showMessage('Importing HAR file...')
        self.import_start = time.time()

        # catch decoding issues
        try:
            with open(self.har_path, 'r', encoding='utf-8-sig') as har_file:
                self.har_raw = json.load(har_file)
        except json.decoder.JSONDecodeError:
            self.app.statusbar.showMessage('[ERROR] Unable to import the selected '
                                           'file due to invalid encoding. Please '
                                           'check the HAR file for errors.')
            raise HarImportException
        except UnicodeDecodeError:
            self.app.statusbar.showMessage('[ERROR] Unable to import the selected file, '
                                           'please open a valid HAR file.')
            raise HarImportException

        # catch syntax issues
        try:
            if not self.har_raw['log']['entries']:
                self.app.statusbar.showMessage('[ERROR] HAR file contains no entries.')
                raise HarImportException
        except KeyError:
            self.app.statusbar.showMessage('[ERROR] HAR file contains no entries.')
            raise HarImportException

    def _parseFile(self):
        """Take the raw HAR file and extract the relevant information to be used
        to populate the entries table and details panels.
        """

        self.har_summary['log_version'] = self.har_raw['log'].get('version', 'Unknown')
        self.har_summary['log_creator_name'] = self.har_raw['log'].get('creator', {}).get('name', 'Unknown')
        self.har_summary['log_creator_version'] = self.har_raw['log'].get('creator', {}).get('version', 'Unknown')
        self.har_summary['browser_name'] = self.har_raw['log'].get('browser', {}).get('name', 'Unknown')
        self.har_summary['browser_version'] = self.har_raw['log'].get('browser', {}).get('version', 'Unknown')

        for entry in self.har_raw['log']['entries']:

            entry_parsed = {}

            entry_parsed['startedDateTime'] = entry.get('startedDateTime', '')
            entry_parsed['time'] = entry.get('time', 0)
            entry_parsed['serverIPAddress'] = entry.get('serverIPAddress', '')
            entry_parsed['connection'] = entry.get('connection', '')

            entry_parsed['request_method'] = entry.get('request', {}).get('method', '')
            entry_parsed['request_url'] = entry.get('request', {}).get('url', '')
            entry_parsed['request_httpVersion'] = entry.get('request', {}).get('httpVersion', '')
            entry_parsed['request_cookies'] = entry.get('request', {}).get('cookies', [])
            entry_parsed['request_headers'] = entry.get('request', {}).get('headers', [])
            entry_parsed['request_queryString'] = entry.get('request', {}).get('queryString', [])
            entry_parsed['request_postData'] = entry.get('request', {}).get('postData', {})
            entry_parsed['request_postData_mimeType'] = entry_parsed['request_postData'].get('mimeType', '')
            entry_parsed['request_postData_params'] = entry_parsed['request_postData'].get('params', [])
            entry_parsed['request_postData_text'] = entry_parsed['request_postData'].get('text', '')
            entry_parsed['request_headersSize'] = entry.get('request', {}).get('headersSize', -1)
            entry_parsed['request_bodySize'] = entry.get('request', {}).get('bodySize', -1)

            entry_parsed['response_status'] = entry.get('response', {}).get('status', -1)
            entry_parsed['response_statusText'] = entry.get('response', {}).get('statusText', '')
            entry_parsed['response_httpVersion'] = entry.get('response', {}).get('httpVersion', '')
            entry_parsed['response_cookies'] = entry.get('response', {}).get('cookies', [])
            entry_parsed['response_headers'] = entry.get('response', {}).get('headers', [])
            entry_parsed['response_content'] = entry.get('response', {}).get('content', [])
            entry_parsed['response_content_size'] = entry_parsed['response_content'].get('size', -1)
            entry_parsed['response_content_compression'] = entry_parsed['response_content'].get('compression', -1)
            entry_parsed['response_content_mimeType'] = entry_parsed['response_content'].get('mimeType', '')
            entry_parsed['response_content_text'] = entry_parsed['response_content'].get('text', '')
            entry_parsed['response_content_encoding'] = entry_parsed['response_content'].get('encoding', '')
            entry_parsed['response_redirectURL'] = entry.get('response', {}).get('redirectURL', '')
            entry_parsed['response_headersSize'] = entry.get('response', {}).get('headersSize', -1)
            entry_parsed['response_bodySize'] = entry.get('response', {}).get('bodySize', -1)

            entry_parsed['cache_beforeRequest_expires'] = entry.get('cache', {}).get('beforeRequest', {}).get('expires','')
            entry_parsed['cache_beforeRequest_lastAccess'] = entry.get('cache', {}).get('beforeRequest', {}).get('lastAccess','')
            entry_parsed['cache_beforeRequest_eTag'] = entry.get('cache', {}).get('beforeRequest', {}).get('eTag','')
            entry_parsed['cache_beforeRequest_hitCount'] = entry.get('cache', {}).get('beforeRequest', {}).get('hitCount',-1)
            entry_parsed['cache_afterRequest_expires'] = entry.get('cache', {}).get('afterRequest', {}).get('expires','')
            entry_parsed['cache_afterRequest_lastAccess'] = entry.get('cache', {}).get('afterRequest', {}).get('lastAccess','')
            entry_parsed['cache_afterRequest_eTag'] = entry.get('cache', {}).get('afterRequest', {}).get('eTag','')
            entry_parsed['cache_afterRequest_hitCount'] = entry.get('cache', {}).get('afterRequest', {}).get('hitCount',-1)

            entry_parsed['timings_blocked'] = entry.get('timings', {}).get('blocked', -1)
            entry_parsed['timings_dns'] = entry.get('timings', {}).get('dns', -1)
            entry_parsed['timings_connect'] = entry.get('timings', {}).get('connect', -1)
            entry_parsed['timings_send'] = entry.get('timings', {}).get('send', -1)
            entry_parsed['timings_wait'] = entry.get('timings', {}).get('wait', -1)
            entry_parsed['timings_receive'] = entry.get('timings', {}).get('receive', -1)
            entry_parsed['timings_ssl'] = entry.get('timings', {}).get('ssl', -1)

            ##################################
            # start of custom HAR parsing logic
            ##################################

            # HAR file may contain invalid field types
            if entry_parsed['time'] is None:
                entry_parsed['time'] = 0
            if entry_parsed['response_bodySize'] is None:
                entry_parsed['response_bodySize'] = -1

            # extract the request protocol
            request_protocol = re.match(r'https?', entry_parsed['request_url'])
            entry_parsed['request_protocol'] = request_protocol.group()

            # extract cookie info from headers if cookies object is empty
            if not entry_parsed['request_cookies']:
                entry_parsed['request_cookies'] = self._parseCookies(entry_parsed['request_headers'])
            if not entry_parsed['response_cookies']:
                entry_parsed['response_cookies'] = self._parseCookies(entry_parsed['response_headers'])

            # SAML requests and responses

            entry_parsed['request_saml'] = ''
            entry_parsed['response_saml'] = ''

            if self.app.config.getConfig('experimental-saml'):
                if entry_parsed['request_queryString']:
                    entry_parsed['request_saml'] = self._parseSaml(entry_parsed['request_queryString'], 'request')
                if entry_parsed['request_postData_text']:
                    entry_parsed['response_saml'] = self._parseSaml(entry_parsed['request_postData_text'], 'response')
                
            # HAR files don't have a unique ID for each request so let's make one to be used
            # for indexing later.
            uid = ''.join(random.choice(string.ascii_lowercase) for i in range(8))

            ##################################
            # end of custom HAR parsing logic
            ##################################

            self.har_parsed[uid] = entry_parsed

        self.app.har_summary = self.har_summary
        self.app.har_parsed = self.har_parsed

    def _populateTable(self):
        """Generate the main entries table from the parsed HAR data."""

        column_details = self.app.config.getConfig('table_columns')
        column_details = sorted(column_details.items(), key=lambda column: column[1]['index'])

        table_headers = [column[1].get('name') for column in column_details]

        self.app.entries_table.setColumnCount(len(table_headers))
        self.app.entries_table.setHorizontalHeaderLabels(table_headers)
        self.app.entries_table.setRowCount(0)

        # disable screen painting until the entry table has been populated.
        self.app.entries_table.setUpdatesEnabled(False)

        row_current = 0

        r = row_current
        t = self.app.entries_table

        for key, value in self.har_parsed.items():
            t.insertRow(r)
            t.setRowHeight(r, 20)
            t.setItem(r, 0, QTableWidgetItem(key))
            t.setItem(r, 1, QTableWidgetItem(str(value['startedDateTime'])))
            t.setItem(r, 2, QTableWidgetItem(str(value['serverIPAddress'])))
            t.setItem(r, 3, QTableWidgetItem(str(value['connection'])))
            t.setItem(r, 4, QTableWidgetItem(str(value['request_method']).upper()))
            t.setItem(r, 5, QTableWidgetItem(str(value['request_protocol']).upper()))
            t.setItem(r, 6, QTableWidgetItem(str(value['request_url'])))
            t.setItem(r, 7, QTableWidgetItem(str(value['request_httpVersion']).upper()))
            t.setItem(r, 8, QTableWidgetItem(str(value['response_status'])))
            t.setItem(r, 9, QTableWidgetItem(str(value['response_statusText'])))
            t.setItem(r, 10, QTableWidgetItem(str(value['response_content_mimeType']).lower()))
            t.setItem(r, 11, QTableWidgetItem(str(value['response_httpVersion']).upper()))
            t.setItem(r, 12, QTableWidgetItem(str(value['response_redirectURL'])))
            t.setItem(r, 13, HTableWidgetItem(str(int(value['request_headersSize'])), value['request_headersSize']))
            t.setItem(r, 14, HTableWidgetItem(str(int(value['request_bodySize'])), value['request_bodySize']))
            t.setItem(r, 15, HTableWidgetItem(str(int(value['response_headersSize'])), value['response_headersSize']))
            t.setItem(r, 16, HTableWidgetItem(str(int(value['response_bodySize'])), value['response_bodySize']))
            t.setItem(r, 17, HTableWidgetItem(str(int(value['response_content_size'])), value['response_content_size']))
            t.setItem(r, 18, HTableWidgetItem(str(int(value['time'])), value['time']))
            t.setItem(r, 19, HTableWidgetItem(str(int(value['timings_blocked'])), value['timings_blocked']))
            t.setItem(r, 20, HTableWidgetItem(str(int(value['timings_dns'])), value['timings_dns']))
            t.setItem(r, 21, HTableWidgetItem(str(int(value['timings_connect'])), value['timings_connect']))
            t.setItem(r, 22, HTableWidgetItem(str(int(value['timings_send'])), value['timings_send']))
            t.setItem(r, 23, HTableWidgetItem(str(int(value['timings_wait'])), value['timings_wait']))
            t.setItem(r, 24, HTableWidgetItem(str(int(value['timings_receive'])), value['timings_receive']))
            t.setItem(r, 25, HTableWidgetItem(str(int(value['timings_ssl'])), value['timings_ssl']))
            r += 1

    def _finalise(self):

        toggleColumnVisibility(self.app)
        resizeColumns(self.app)

        if self.app.config.getConfig('cell-colorization'):
            colourizeCells(self.app)

        self.app.global_searchbox.setReadOnly(False)
        self.app.request_filter.setReadOnly(False)
        self.app.response_filter.setReadOnly(False)

        self.app.request_tabs.setTabEnabled(0, True)
        self.app.response_tabs.setTabEnabled(0, True)

        self.app.entries_table.setSortingEnabled(True)
        self.app.entries_table.scrollToTop()
        self.app.entries_table.selectRow(0)
        self.app.entries_table.setFocus()

        # turn screen paining back on
        self.app.entries_table.setUpdatesEnabled(True)

        row_count = self.app.entries_table.rowCount()
        import_stop = time.time()
        elapsed_time = import_stop - self.import_start

        self.app.statusbar.showMessage('[OK] Imported {} entries in {:.1f} seconds'.format(row_count, elapsed_time))
        self.app.setWindowTitle('Harshark 2.0.0 (dev) | HTTP Archive (HAR) Viewer | {}'.format(self.har_path))

    @staticmethod
    def _parseCookies(headers):
        """If there is no cookie object included for a request/response, try to construct
        one from the HTTP headers if we find Cookie or Set-Cookie headers.
        """
        cookie_object = []

        for header in headers:
            if header['name'].lower() == 'cookie':
                cookie_object.append(header['value'].split('; '))
            elif header['name'].lower() == 'set-cookie':
                cookie_object.append(header['value'].split('\n'))

        cookie_object = [item for sublist in cookie_object for item in sublist]
        return cookie_object

    @staticmethod
    def _parseSaml(saml, saml_type):
        """Decode any SAML request/response messages found in  the query string (HTTP-Redirect binding)
        or body text (HTTP-POST binding).
        """
        if saml_type == 'request':
            for param in saml:
                if param['name'].lower() == 'samlrequest':
                    request_decoded = b64decode(param['value'])
                    request_decompressed = decompress(request_decoded, -15).decode('utf-8')
                    return request_decompressed

        elif saml_type == 'response':
            # TODO: what if we don't have a relaystate included? Regex needs improved.
            saml_response = re.search(r'(?<=SAMLResponse\=).+(?=\&RelayState.+)', saml)
            if saml_response:
                response_encoded = saml_response.group().replace('%2B', '+')
                response_decoded = b64decode(response_encoded).decode('utf-8')
                return response_decoded

        return ''


class HTableWidgetItem(QTableWidgetItem):
    """Reimplement QTableWidgetItem to allow sorting of numeric columns."""
    def __init__(self, text, sortKey):
        QTableWidgetItem.__init__(self, text, QTableWidgetItem.UserType)
        self.sortKey = sortKey

    def __lt__(self, other):
        try:
            return self.sortKey < other.sortKey
        except TypeError:
            return -1
