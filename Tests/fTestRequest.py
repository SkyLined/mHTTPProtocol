from mHTTPProtocol import cHTTPRequest, cHTTPHeader, cHTTPHeaders;

def fTestRequest():
  
  for oRequest in [
    cHTTPRequest(
      sbURL = b"http://example.com",
      sbzMethod = b"GET",
      sbzVersion = b"HTTP/1.0",
      o0zHeaders = cHTTPHeaders(),
      sb0Body = b"Body",
    ),
    cHTTPRequest(
      sbURL = b"http://example.com",
      sbzMethod = b"GET",
      sbzVersion = b"HTTP/1.0",
      o0zHeaders = cHTTPHeaders(),
      s0Data = "Body",
    ),
    cHTTPRequest(
      sbURL = b"http://example.com",
      sbzMethod = b"GET",
      sbzVersion = b"HTTP/1.1",
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
