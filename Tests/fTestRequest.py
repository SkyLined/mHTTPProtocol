from mHTTPProtocol import cRequest, cHeader, cHeaders;

def fTestRequest(bRunFullTests):
  oRequest1 = cRequest(
    sbURL = b"http://example.com",
    sbzMethod = b"GET",
    sbzVersion = b"HTTP/1.0",
    o0zHeaders = cHeaders(),
    sbBody = b"Body 1",
  );
  
  oRequest1x = oRequest1.foClone();
  oRequest1x.fSetBodyChunks(
    asbData = [b"Body", b" 1x"],
    bSetChunkedEncodingHeader = True,
    bRemoveContentLengthHeaders = True,
  );
  
  oRequest2 = cRequest(
    sbURL = b"http://example.com",
    sbzMethod = b"GET",
    sbzVersion = b"HTTP/1.1",
    o0zHeaders = cHeaders(
      aoHeaders = [
        cHeader(b"Transfer-Encoding", b"chunked"),
      ]
    ),
  );
  oRequest2.fSetBodyChunks(
    asbData = [b"Body", b" 2"],
  );
  oChunkedRequest1 = cRequest(
    sbURL = b"http://example.com",
    sbzMethod = b"GET",
    sbzVersion = b"HTTP/1.1",
  );
  oChunkedRequest1.fSetBodyChunks(
    asbData = [b"Body", b" chunked ", b"1"],
    bSetChunkedEncodingHeader = True,
  );
  
  oChunkedRequest1b = oChunkedRequest1.foClone();
  oChunkedRequest1b.fAddBodyChunk(b"b");
  
  oChunkedRequest1c = oChunkedRequest1b.foClone();
  oChunkedData = oChunkedRequest1c.foGetChunkedData();
  oChunkedData.aoChunks[-1].sbData = b"c";
  oChunkedData.aoChunks[-1].dsb0ExtensionValue_by_sbName[b"Extension Name"] = b"Extension Value";
  oChunkedData.oTrailers.foAddNameAndValue(b"Trailer Name", b"Trailer Value");
  oChunkedRequest1c.fSetBody(oChunkedData.fsbSerialize());
  sbBody = oChunkedRequest1c.fsbGetBody();
  assert sbBody == b"4\r\nBody\r\n9\r\n chunked \r\n1\r\n1\r\n1; Extension Name=Extension Value\r\nc\r\n0\r\nTrailer Name: Trailer Value\r\n\r\n", \
      f"Got {repr(sbBody)}";
  oChunkedRequest1c.foGetChunkedData();
  
  oDechunkedRequest = oChunkedRequest1b.foClone();
  oDechunkedRequest.fSetBody(
    sbData = b"Body dechunked",
    bRemoveChunkedEncodingHeaders = True,
    bSetContentLengthHeader = True,
  );
  
  oRequest3 = cRequest(
    sbURL = b"http://example.com",
    sbzMethod = b"GET",
    sbzVersion = b"HTTP/1.0",
    o0zHeaders = cHeaders(),
    sbBody = b"Body 3",
    bSetContentLengthHeader = True,
  );
  
  
  for (sExpectedData, oRequest) in {
    "Body 1": oRequest1,
    "Body 1x": oRequest1x,
    "Body 2": oRequest2,
    "Body chunked 1": oChunkedRequest1,
    "Body chunked 1b": oChunkedRequest1b,
    "Body chunked 1c": oChunkedRequest1c,
    "Body dechunked": oDechunkedRequest,
    "Body 3": oRequest3,
  }.items():
    sData = oRequest.fsGetDecodedAndDecompressedBody();
    assert sData == sExpectedData, \
          "Data not as expected!\nData:     %s\nExpected: %s" % (repr(sData), repr(sExpectedData));
    sbRequest = oRequest.fsbSerialize();
    oClone = oRequest.foClone();
    sbClone = oClone.fsbSerialize()
    assert sbRequest == sbClone, \
          "Clone not as expected!\nRequest:  %s\nClone:    %s" % (repr(sbRequest)[1:], repr(sbClone)[1:]);

  