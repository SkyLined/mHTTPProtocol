Implementation of HTTP protocol. Can be used to make HTTP requests over a
TCP/IP connection.

`iHTTPMessage`
--------------
Interface defining the majority of HTTP protocol features, used as a base class
for `cHTTPRequest` and `cHTTPResponse`.

`cHTTPRequest`
--------------
Represents a single HTTP request.

`cHTTPResponse`
--------------
Represents a single HTTP response.

`cURL`
------
Represents a single URL.

`cHTTPHeaders`
--------------
Respesents a collection of HTTP headers, used by `iHTTPMessage` to represent
the HTTP headers found in a HTTP message.

`cHTTPHeader`
-------------
Respesents a single HTTP header. Used by `cHTTPHeaders` to store individual
headers.
