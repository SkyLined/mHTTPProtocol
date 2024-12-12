from mHTTPProtocol import cHTTPResponse, cHTTPHeader, cHTTPHeaders;

def fTestResponse():
  
  for oRequest in [
    cHTTPResponse(
      sbzVersion = b"HTTP/1.0",
      uzStatusCode = 200,
      sbzReasonPhrase = b"OK",
      o0zHeaders = cHTTPHeaders(),
      sb0Body = b"Body",
      bAddContentLengthHeader = False,
      bAddConnectionCloseHeader = True,
    ),
    cHTTPResponse(
      sbzVersion = b"HTTP/1.0",
      uzStatusCode = 404,
      sbzReasonPhrase = b"Not Found",
      o0zHeaders = cHTTPHeaders(),
      s0Data = "Body",
    ),
    cHTTPResponse(
      sbzVersion = b"HTTP/1.1",
      uzStatusCode = 500,
      sbzReasonPhrase = b"Internal server error",
      o0zHeaders = cHTTPHeaders(
        a0oHeaders = [
          cHTTPHeader(b"Transfer-Encoding", b"chunked"),
        ]
      ),
      a0sbBodyChunks = [b"Body"],
    ),
  ]:
    sbRequest = oRequest.fsbSerialize();
    oClone = oRequest.foClone();
    sbClone = oClone.fsbSerialize()
    assert sbRequest == sbClone, \
        sbRequest + sbClone;
