Branch Testing
More Testing

# Harshark

Harshark is a simple, offline HTTP Archive (HAR) file viewer built with Python 3.
It is compatible with version 1.1 or 1.2 HAR files and should be able to open
captures taken directly from Chrome, Firefox and newer versions of IE which now
correctly saves network captures as JSON rather than XML.

## Installation

**Python Version**: Python 3 (tested on 3.5.2 and 3.6.1)  
**Dependencies**: PyQt5, sip

You can install the dependencies using [pip3](https://pip.pypa.io/en/stable/installing/) 
and the included `requirements.txt` file:
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
| File > Open  | Open a new HAR file to view (CTRL + O).  |
| File > Exit  | Exit Harshark (CTRL + Q).  |
| Options > Choose Font  | Select the font used to display HAR data.  |
| Options > Choose Highlight Colour | Select the colour used to highlight search results.  |
| Help > About | Software information.  |

### Toolbar

| Item  | Description |
| ------------- | ------------- |
| Open  | Open a new HAR file to view (CTRL + O).  |
| Delete Row  | Delete the currently selected row(s) from the entries table.  |
| Resize Columns to Fit  | Resize all columns in the entries table to fit their content. The 'Request URL' column will be truncated.  |
| Toggle Word Wrap | Toggle word wrapping in the Request and Response panels (enabled by default). |
| Display all Body Content | Show all request/response body content of the currently selected entry if it has been automatically truncated.  |
| Display Mode | Set whether request/response details are displayed inline (Compact) or on a new line (Spaced).  |
| Search  | Search in the Entries table and Request/Response data for matches. |
| Search Mode  | Choose to either highlight (default) or filter search results.  |
| Toggle Case Sensitive Matching  | Toggle whether search queries are case sensitive (default is non case sensitive).  |
| Previous Match  | Jump to the previous search result (Shift + F3).  |
| Next Match  | Jump to the next search result (F3).  |
| Clear Search Results  | Remove all search highlights and filters.  |

### Entries Table

The entries table shows basic information about each request found in the HAR file.

| Column  | Description |
| ------------- | ------------- |
| Timestamp  | Date and time stamp of the request start.  |
| Request Time  | Total elapsed time of the request in milliseconds.  |
| Server IP  | IP address of the server that was connected (result of DNS resolution).  |
| Request Method  | Request method (GET, POST, ...).  |
| Request URL  | Absolute URL of the request.  |
| Response Code  | Response status (200, 403, ...).  |
| HTTP Version  | Response HTTP Version.  |
| Mime Type  | MIME type of the response text (value of the Content-Type response header).  |
| Request Header Size  | Total number of bytes from the start of the HTTP request message up to (and including) the double CRLF before the body.  |
| Request Body Size  | Size of the request body (POST data payload) in bytes.  |
| Response Header Size  | Total number of bytes from the start of the HTTP response message up to (and including) the double CRLF before the body.  |
| Response Body Size  | Size of the received response body in bytes. Set to zero in case of responses coming from the cache (304).  |

### Request & Response Panels

The Request & Response panels display detailed information about the currently 
selected request: HTTP Headers, Body Content, Query Strings and Cookies.

You can enter a search query in the built-in search box which will highlight any
matches found within the currently selected tab. Press F5 and F6 to jump to the 
next search match in the Request and Response panel respectively.

Search results can be cleared by either entering a blank search query, selecting
a new request in the entries table or clicking the 'Clear Search Results' button
on the toolbar.

The 'Toggle Case Sensitive Matching' option controls the search functionality
of both the main entries table and the request/response details panels.

For best performance, try to avoid very short search queries.