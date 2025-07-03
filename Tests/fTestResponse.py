from mHTTPProtocol import cResponse, cHeader, cHeaders;

def fTestResponse(bRunFullTests):
  
  for oRequest in [
    cResponse(
      sbzVersion = b"HTTP/1.0",
      uzStatusCode = 200,
      sbzReasonPhrase = b"OK",
      o0zHeaders = cHeaders(),
      sbBody = b"Body",
    ),
    cResponse(
      sbzVersion = b"HTTP/1.0",
      uzStatusCode = 404,
      sbzReasonPhrase = b"Not Found",
      o0zHeaders = cHeaders(),
      sbBody = b"Body",
      bSetContentLengthHeader = True,
    ),
    cResponse(
      sbzVersion = b"HTTP/1.1",
      uzStatusCode = 500,
      sbzReasonPhrase = b"Internal server error",
      sbBody = b"Body",
    ),
  ]:
    sbRequest = oRequest.fsbSerialize();
    oClone = oRequest.foClone();
    sbClone = oClone.fsbSerialize()
    assert sbRequest == sbClone, \
        sbRequest + sbClone;
