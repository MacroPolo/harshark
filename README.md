# Harshark

Harshark is a simple, offline HTTP Archive (HAR) parser built with Python 3 which will allow you to 
quickly analyse HAR captures as part of your troubleshooting toolkit. It is compatible with version 
1.1 or 1.2 HAR files and should be able to open captures taken directly from Chrome, Firefox and 
newer versions of Internet Explorer which now correctly saves network captures as JSON rather than XML.

## Installation

**Python Version**: Python 3.5 or above
**Dependencies**: beautifulsoup4, PyQt5, lxml

To install, you can simply clone this repository and then install the dependencies.
```
git clone https://github.com/MacroPolo/harshark.git
pip3 install -r requirements.txt
```

## Usage
```bash
$ python3 src/harshark.py
```
## User Guide

### Main Menu

| Item  | Description |
| ------------- | ------------- |
| File > Open  | Open a new HAR file to view (CTRL + O).  |
| File > Exit  | Exit Harshark (CTRL + Q).  |
| View > Word Wrap  | Toggle word wrapping in the entry detail panels.  |
| File > Sort Headers  | Toggle alphabetically sorted HTTP request and response headers.  |
| File > Cell Colourization  | Toggle cell colourizations.  |
| File > Resize Columns  | Resize columns to fit.  |
| Options > Choose Columns  | Select which columns to display in the entries table.  |
| Options > SAML Parsing  | Enable or disable the parsing of SAML Request and Response content.  |
| Help > About | Software information.  |

### Toolbar

| Item  | Description |
| ------------- | ------------- |
| Open  | Open a new HAR file to view (CTRL + O).  |
| Toggle Case Sensitive Searching  | Default is non case-sensitive matching.  |
| Next Match  | Jump to the next search result in the entries table (F3).  |
| Clear Search Results  | Remove all search highlights from the entries table.  |

### Entries Table

The entries table shows information about each request found in the HAR file. Column descriptions have been derived from the official HAR specification [here](http://www.softwareishard.com/blog/har-12-spec/#response).

| Column  | Description |
| ------------- | ------------- |
| Timestamp  | Date and time stamp of the request start (ISO 8601 - YYYY-MM-DDThh:mm:ss.sTZD).  |
| Server IP  | IP address of the server that was connected (result of DNS resolution).  |
| Connection ID  | Unique ID of the parent TCP/IP connection, can be the client or server port number.  |
| Method  | Request method (GET, POST, ...).  |
| Protocol  | Request protocol used (HTTP, HTTPS).  |
| Hostname  | Server hostname.  |
| Port  | Destination port.  |
| Path  | Hierarchical URL path.  |
| Full URL  | Absolute URL of the request (fragments are not included).  |
| HTTP Version (Request) | Request HTTP Version.  |
| Status Code  | Response status (200, 403, ...).  |
| Status Text  | Response status description.  |
| Mime Type  | MIME type of the response text (value of the Content-Type response header).  |
| HTTP Version (Response) | Response HTTP Version.  |
| Redirect URL | Redirection target URL from the Location response header.  |
| Request Header Size  | Total number of bytes from the start of the HTTP request message up to (and including) the double CRLF before the body.  |
| Request Body Size  | Size of the request body (POST data payload) in bytes.  |
| Response Header Size  | Total number of bytes from the start of the HTTP response message up to (and including) the double CRLF before the body.  |
| Response Body Size  | Size of the received response body in bytes. Set to zero in case of responses coming from the cache (304).  |
| Response Body Size (Uncompressed)  | Length of the returned content in bytes. Should be equal to Response Body Size if there is no compression and bigger when the content has been compressed.  |
| Time Total  | Total elapsed time of the request in milliseconds.  |
| Time Blocked  | Time spent in a queue waiting for a network connection.  |
| Time DNS  | DNS resolution time. The time required to resolve a host name.  |
| Time Connect  | Time required to create TCP connection.  |
| Time Send  | Time required to send HTTP request to the server.  |
| Time Wait  | Waiting for a response from the server.  |
| Time Receive  | Time required to read entire response from the server (or cache).  |
| Time SSL  | Time required for SSL/TLS negotiation.  |

### Searching

Using the search bar above the entries table will perform a global search across all entries and 
highlight any rows which contain at least one match. Searches performed within the global search 
bar can optionally be made case-sensitive by clicking the toggle button to the left of the search 
bar.

There is also search functionality built into the request and response panels which allow you to 
perform a more focused search on the current aspect of the entry that you are interested in. For 
example, you can perform a search from within the Response Body tab which will highlight any 
matches and allow you to navigate between them.

For best performance, try to avoid very short search queries.