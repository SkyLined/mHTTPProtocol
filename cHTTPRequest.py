from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
from .cHTTPHeaders import cHTTPHeaders;
from .iHTTPMessage import iHTTPMessage;
from cURL import cURL;

class cHTTPRequest(iHTTPMessage):
  cURL = cURL;
  
  @staticmethod
  @ShowDebugOutput
  def fdxParseStatusLine(sStatusLine):
    asComponents = sStatusLine.split(" ", 2);
    if len(asComponents) != 3:
      raise iHTTPMessage.cInvalidMessageException("The remote send an invalid status line.", sStatusLine);
    sMethod, sURL, sVersion = asComponents;
    if sVersion not in ["HTTP/1.0", "HTTP/1.1"]:
      raise iHTTPMessage.cInvalidMessageException("The remote send an invalid HTTP version in the status line.", sVersion);
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    return {"szMethod": sMethod, "sURL": sURL, "szVersion": sVersion};
  
  @ShowDebugOutput
  def __init__(oSelf, sURL, szMethod = None, szVersion = None, ozHeaders = None, szBody = None, szData = None, azsBodyChunks = None, ozAdditionalHeaders = None):
    oSelf.__sURL = sURL;
    oSelf.__sMethod = szMethod or ("POST" if (szBody or szData or azsBodyChunks) else "GET");
    oHeaders = ozHeaders or cHTTPHeaders.foFromDict({
      "Accept": "*/*",
      "Accept-Encoding": ", ".join(oSelf.asSupportedCompressionTypes),
      "Cache-Control": "No-Cache, Must-Revalidate",
      "Connection": "Keep-Alive",
      "Pragma": "No-Cache",
    });
    iHTTPMessage.__init__(oSelf, szVersion, oHeaders, szBody, szData, azsBodyChunks, ozAdditionalHeaders);
  
  @property
  def sURL(oSelf):
    return oSelf.__sURL;
  @sURL.setter
  def sURL(oSelf, sURL):
    oSelf.__sURL = sURL;
  @property
  def sMethod(oSelf):
    return oSelf.__sMethod;
  @sMethod.setter
  def sMethod(oSelf, sMethod): # Setting to None or "" results in "POST" if there is a body and "GET" if there is none.
    oSelf.__sMethod = sMethod or ("POST" if (szBody or szData or azsBodyChunks) else "GET");
  
  @ShowDebugOutput
  def foClone(oSelf):
    if oSelf.bChunked:
      return cHTTPRequest(oSelf.sURL, oSelf.sMethod, oSelf.sVersion, oSelf.oHeaders.foClone(), azsBodyChunks = oSelf.azsBodyChunks);
    return cHTTPRequest(oSelf.sURL, oSelf.sMethod, oSelf.sVersion, oSelf.oHeaders.foClone(), szBody = oSelf.szBody);
  
  def fsGetStatusLine(oSelf):
    return "%s %s %s" % (oSelf.sMethod, oSelf.sURL, oSelf.sVersion);
  
  @ShowDebugOutput
  def foCreateReponse(oSelf,
    uzStatusCode = None, szMediaType = None, szBody = None,
    szVersion = None, szReasonPhrase = None, ozHeaders = None, szData = None, azsBodyChunks = None, szCharSet = None
  ):
    uStatusCode = uzStatusCode or 200;
    sVersion = szVersion or oSelf.sVersion;
    szMediaType = szMediaType if szMediaType else "text/plain" if (szBody or szData or axsBodyChunks) else None;
    oHeaders = oHeaders or cHTTPHeaders.foDefaultHeadersForVersion(sVersion);
    oResponse = cHTTPResponse(
      sVersion = sVersion,
      uStatusCode = uStatusCode,
      sReasonPhrase = sReasonPhrase,
      oHeaders = oHeaders,
      sBody = sBody,
      sData = sData,
      asBodyChunks = asBodyChunks,
    );
    if szMediaType:
      assert isinstance(szMediaType, (str, unicode)), \
          "szMediaType must be a string or None, not %s" % repr(sMediaType);
      oResponse.szMediaType = str(szMediaType);
      if szCharSet:
        assert isinstance(szCharSet, (str, unicode)), \
            "szCharSet must be a string or None, not %s" % repr(szCharSet);
        oResponse.szCharSet = str(szCharSet);
    return oResponse;
  
