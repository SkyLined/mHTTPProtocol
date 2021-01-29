import re;

try: # mDebugOutput use is Optional
  from mDebugOutput import *;
except: # Do nothing if not available.
  ShowDebugOutput = lambda fxFunction: fxFunction;
  fShowDebugOutput = lambda sMessage: None;
  fEnableDebugOutputForModule = lambda mModule: None;
  fEnableDebugOutputForClass = lambda cClass: None;
  fEnableAllDebugOutput = lambda: None;
  cCallStack = fTerminateWithException = fTerminateWithConsoleOutput = None;

from .cHTTPHeaders import cHTTPHeaders;
from .cHTTPResponse import cHTTPResponse;
from .iHTTPMessage import iHTTPMessage;
from .cURL import cURL;
from .fsDecompressData import fsDecompressData;
from .mExceptions import *;
from .mNotProvided import *;

gsSupportedCompressionTypes= ", ".join(fsDecompressData.asSupportedCompressionTypes);
gsUserAgent = "Mozilla/5.0 (compatible)";

class cHTTPRequest(iHTTPMessage):
  ddDefaultHeader_sValue_by_sName_by_sHTTPVersion = {
    "HTTP/1.0": {
      "Accept": "*/*",
      "Accept-Encoding": gsSupportedCompressionTypes,
      "Connection": "Close",
      "User-Agent": gsUserAgent,
    },
    "HTTP/1.1": {
      "Accept": "*/*",
      "Accept-Encoding": gsSupportedCompressionTypes,
      "Cache-Control": "No-Cache, Must-Revalidate",
      "Connection": "Keep-Alive",
      "User-Agent": gsUserAgent,
    },
  };
  
  @staticmethod
  @ShowDebugOutput
  def fdxParseStatusLine(sStatusLine):
    asComponents = sStatusLine.split(" ", 2);
    if len(asComponents) != 3:
      raise cHTTPInvalidMessageException("The remote send an invalid status line.", sStatusLine);
    sMethod, sURL, sVersion = asComponents;
    if sVersion not in ["HTTP/1.0", "HTTP/1.1"]:
      raise cHTTPInvalidMessageException("The remote send an invalid HTTP version in the status line.", sVersion);
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    return {"szMethod": sMethod, "sURL": sURL, "szVersion": sVersion};
  
  @ShowDebugOutput
  def __init__(oSelf,
    sURL,
    szMethod = zNotProvided,
    szVersion = zNotProvided,
    o0zHeaders = zNotProvided,
    s0Body = None,
    s0Data = None,
    a0sBodyChunks = None,
    o0AdditionalHeaders = None,
    bAutomaticallyAddContentLengthHeader = False
  ):
    oSelf.__sURL = sURL;
    oSelf.__sMethod = fxGetFirstProvidedValue(szMethod, "POST" if (s0Body or s0Data or a0sBodyChunks) else "GET");
    iHTTPMessage.__init__(oSelf,
      szVersion,
      o0zHeaders,
      s0Body,
      s0Data,
      a0sBodyChunks,
      o0AdditionalHeaders,
      bAutomaticallyAddContentLengthHeader
    );
  
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
  def sMethod(oSelf, sMethod):
    assert isinstance(sMethod, str) and re.match("^[A-Z]+$", sMethod), \
        "The reason phrase must be a 'str' with one or more uppercase letters, not %s" % repr(sReasonPhrase);
    oSelf.__sMethod = sMethod;
  
  @ShowDebugOutput
  def foClone(oSelf):
    if oSelf.bChunked:
      return cHTTPRequest(oSelf.sURL, oSelf.sMethod, oSelf.sVersion, oSelf.oHeaders.foClone(), a0sBodyChunks = oSelf.a0sBodyChunks);
    return cHTTPRequest(oSelf.sURL, oSelf.sMethod, oSelf.sVersion, oSelf.oHeaders.foClone(), s0Body = oSelf.s0Body);
  
  def fsGetStatusLine(oSelf):
    return "%s %s %s" % (oSelf.sMethod, oSelf.sURL, oSelf.sVersion);
  
  @ShowDebugOutput
  def foCreateReponse(oSelf,
    szVersion = zNotProvided,
    uzStatusCode = zNotProvided,
    szReasonPhrase = zNotProvided,
    o0zHeaders = zNotProvided,
    s0Body = None,
    s0Data = None,
    a0sBodyChunks = None,
    s0CharSet = None,
    o0AdditionalHeaders = None,
    s0MediaType = None,
    bAutomaticallyAddContentLengthHeader = False
  ):
    sVersion = fxGetFirstProvidedValue(szVersion, oSelf.sVersion);
    oResponse = cHTTPResponse(
      szVersion = sVersion,
      uzStatusCode = uzStatusCode,
      szReasonPhrase = szReasonPhrase,
      o0zHeaders = o0zHeaders,
      s0Body = s0Body,
      s0Data = s0Data,
      a0sBodyChunks = a0sBodyChunks,
      o0AdditionalHeaders = o0AdditionalHeaders,
      bAutomaticallyAddContentLengthHeader = bAutomaticallyAddContentLengthHeader,
    );
    if s0MediaType or s0Body or s0Data or a0sBodyChunks:
      assert s0MediaType is None or isinstance(s0MediaType, (str, unicode)), \
          "s0MediaType must be a string or None, not %s" % repr(s0MediaType);
      oResponse.s0MediaType = str(s0MediaType or "application/octet-stream");
      if s0CharSet:
        assert isinstance(s0CharSet, (str, unicode)), \
            "s0CharSet must be a string or None, not %s" % repr(s0CharSet);
        oResponse.s0CharSet = str(s0CharSet);
    else:
      assert s0CharSet is None, \
          "s0CharSet (%s) cannot be defined is s0MediaType is None!" % repr(s0CharSet);
    return oResponse;
  
