import codecs
import json
import random
import sqlite3
import string

class HarParse():

    def __init__(self, harfile=''):
        self.har_file = harfile
        self.har_db = 'har.db'
        self.id = ''
        
        self.conn = sqlite3.connect(self.har_db)
        self.c = self.conn.cursor()

        self.initDb()
        self.parse()

    def initDb(self):

        try:
            self.c.execute('DROP TABLE requests')
        except sqlite3.OperationalError:
            pass

        self.c.execute('''CREATE TABLE IF NOT EXISTS requests
        (id                     TEXT            PRIMARY KEY,
        timestamp               DATETIME,
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
        request_header_size     TEXT,
        request_body            TEXT,
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

        self.conn.commit()

        self.db_fields = {
            'timestamp':'', 
            'time':'', 
            'server_ip':'', 
            'port':'', 
            'request_body_size':'', 
            'request_method':'', 
            'request_url':'', 
            'request_http_version':'',
            'request_headers':'', 
            'request_cookies':'', 
            'request_query_string':'', 
            'request_header_size':'',
            'request_post_body':'', 
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

    def generateId(self):
        id = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(5))
        self.id = id


    def keyCheck(self, db_field, har_field, har_section):
        try:
            self.db_fields[db_field] = str(har_section[har_field])
        except KeyError:
            pass


    def parse(self):
        with open(self.har_file, encoding='utf-8') as har:    
            har = json.load(har)
    
        self.c.execute('BEGIN TRANSACTION')

        for entry in har['log']['entries']:
            self.generateId()
            self.keyCheck('timestamp', 'startedDateTime', entry)
            self.keyCheck('time', 'time', entry)            
            self.keyCheck('server_ip', 'serverIPAddress', entry)
            self.keyCheck('port', 'connection', entry)
            self.keyCheck('request_body_size', 'bodySize', entry['request'])
            self.keyCheck('request_method', 'method', entry['request'])
            self.keyCheck('request_url', 'url', entry['request'])
            self.keyCheck('request_http_version', 'httpVersion', entry['request'])
            self.keyCheck('request_header_size', 'headersSize', entry['request'])
            self.keyCheck('request_headers', 'headers', entry['request'])
            self.keyCheck('request_cookies', 'cookies', entry['request'])
            self.keyCheck('request_query_string', 'queryString', entry['request'])
            self.keyCheck('request_post_body', 'postData', entry['request'])
            self.keyCheck('response_status', 'status', entry['response'])
            self.keyCheck('response_status_text', 'statusText', entry['response'])
            self.keyCheck('response_http_version', 'httpVersion', entry['response'])
            self.keyCheck('response_headers', 'headers', entry['response'])
            self.keyCheck('response_cookies', 'cookies', entry['response'])
            self.keyCheck('response_body', 'content', entry['response'])
            self.keyCheck('response_redirect_url', 'redirectURL', entry['response'])
            self.keyCheck('response_headers_size', 'headersSize', entry['response'])
            self.keyCheck('response_body_size', 'bodySize', entry['response'])
            self.keyCheck('timings_blocked', 'blocked', entry['timings'])
            self.keyCheck('timings_dns', 'dns', entry['timings'])
            self.keyCheck('timings_connect', 'connect', entry['timings'])
            self.keyCheck('timings_send', 'send', entry['timings'])
            self.keyCheck('timings_wait', 'wait', entry['timings'])
            self.keyCheck('timings_receive', 'receive', entry['timings'])
            self.keyCheck('timings_ssl', 'ssl', entry['timings'])
            self.updateDb()

        self.c.execute('COMMIT')
        self.conn.close()

    def updateDb(self):

        self.c.execute("INSERT INTO requests \
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                                ?, ?, ?, ?, ?, ?)",
                    (self.id,
                    self.db_fields['timestamp'],
                    self.db_fields['time'],
                    self.db_fields['server_ip'],
                    self.db_fields['port'],
                    self.db_fields['request_body_size'],
                    self.db_fields['request_method'],
                    self.db_fields['request_url'],
                    self.db_fields['request_http_version'],
                    self.db_fields['request_headers'],
                    self.db_fields['request_cookies'],
                    self.db_fields['request_query_string'],
                    self.db_fields['request_header_size'],
                    self.db_fields['request_post_body'],
                    self.db_fields['response_status'],
                    self.db_fields['response_status_text'],
                    self.db_fields['response_http_version'],
                    self.db_fields['response_headers'],
                    self.db_fields['response_cookies'],
                    self.db_fields['response_body'],
                    self.db_fields['response_redirect_url'],
                    self.db_fields['response_headers_size'],
                    self.db_fields['response_body_size'],
                    self.db_fields['timings_blocked'],
                    self.db_fields['timings_dns'],
                    self.db_fields['timings_connect'],
                    self.db_fields['timings_send'],
                    self.db_fields['timings_wait'],
                    self.db_fields['timings_receive'],
                    self.db_fields['timings_ssl']
                    ))