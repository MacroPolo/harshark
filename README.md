# Harshark

Harshark is a simple, offline HTTP Archive (HAR) file viewer built with Python 3.

## Installation

**Python Version**: Python 3 (tested on 3.5.2 and 3.6.1)
**Dependancies**: PyQt5, sip

You can install the dependancies with pip3 and the included requirements.txt file:
```
pip3 install -r requirements.txt
```

## Usage
```bash
$ python3 harshark.py
```
## User Guide

### Main Menu

| Item  | Description |
| ------------- | ------------- |
| File > Open  | Open a new HAR file (CTRL + O)  |
| File > Exit  | Exit Harshark (CTRL + Q)  |
| Options > Choose Font  | Select the font used to display data from the HAR file  |
| Option > Choose Highlight Colour | Select the colour used to highlight search 
matches  |
| Help > About | Software information  |

### Toolbar

| Item  | Description |
| ------------- | ------------- |
| Open  | Open a new HAR file (CTRL + O)  |
| Delete Row  | Delete the currently selected row from the entries table  |
| Resize Columns to Fit  | Resize the columns in the entries table to fit their 
content. The Request URL column will not expand fully.  |
| Toggle Word Wrap | Toggle whether the text in the Request and Response panels 
is wrapped (enabled by default) |
| Display all Body Content | Show all request/response body content of the 
currently selected entry if it has been automatically truncated.  |
| Display Mode | Set whether request/response details are displayed inline 
(Compact mode - default) or on a new line (Spaced mode)  |
| Search  | Enter seach query which will be checked against all entries  |
| Search Mode  | Choose to either highlight (default) or filter search results  |
| Toggle Case Sensitive Matching  | Toggle whether search queries are case sensitive 
(default is non case sensitive)  |
| Previous Match  | Jump to the next search result (F4)  |
| Next Match  | Jump to the next search result (F3)  |
| Clear Search Results  | Remove all search highlights or filters  |

### Entires Table

The entries table shows basic information about each request found in the HAR file.

| Column  | Description |
| ------------- | ------------- |
| Timestamp  | Date and time stamp of the request start  |
| Request Time  | Total elapsed time of the request in milliseconds  |
| Server IP  | IP address of the server that was connected (result of DNS resolution)  |
| Request Method  | Request method (GET, POST, ...)  |
| Request URL  | Absolute URL of the request  |
| Response Code  | Response status (200, 403, ...)  |
| HTTP Version  | Response HTTP Version  |
| Mime Type  | MIME type of the response text (value of the Content-Type response 
header)  |
| Request Header Size  | Total number of bytes from the start of the HTTP request 
message up to (and including) the double CRLF before the body.  |
| Request Body Size  | Size of the request body (POST data payload) in bytes.  |
| Response Header Size  | Total number of bytes from the start of the HTTP response 
message up to (and including) the double CRLF before the body  |
| Response Body Size  | Size of the received response body in bytes. Set to zero 
in case of responses coming from the cache (304)  |

### Request & Response Panels

The Request & Response panels display detailed information about the currently 
selected request; HTTP Headers, Body Content, Query Strings and Cookies.

You can enter a search query in the built-in searchbox which will highlight any
matches found within the currently selected tab. Press F5 and F6 to jump to the 
next search match in the Request and Response panel respectively.

Search results can be cleared by either entering a blank search query or selecting
a new request in the entries table.

The 'Toggle Case Sensitive Matching' option also controls the Request/Response 
search functionality.

For best performance, use as verbose a search term as possible.