import re, urllib.parse;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

from mNotProvided import *;

from .cHTTPHeaders import cHTTPHeaders;
from .cHTTPResponse import cHTTPResponse;
from .iHTTPMessage import iHTTPMessage;
from .cURL import cURL;
from .fsbDecompressData import fsbDecompressData;
from .mExceptions import *;

gsbSupportedCompressionTypes= b", ".join(fsbDecompressData.asbSupportedCompressionTypes);
gsbUserAgent = b"Mozilla/5.0 (compatible)";

class cHTTPRequest(iHTTPMessage):
  ddDefaultHeader_sbValue_by_sbName_by_sbHTTPVersion = {
    b"HTTP/1.0": {
      b"Accept": b"*/*",
      b"Accept-Encoding": gsbSupportedCompressionTypes,
      b"Connection": b"Close",
      b"User-Agent": gsbUserAgent,
    },
    b"HTTP/1.1": {
      b"Accept": b"*/*",
      b"Accept-Encoding": gsbSupportedCompressionTypes,
      b"Cache-Control": b"No-Cache, Must-Revalidate",
      b"Connection": b"Keep-Alive",
      b"User-Agent": gsbUserAgent,
    },
  };
  
  @staticmethod
  @ShowDebugOutput
  def fdxParseStatusLine(sbStatusLine, o0Connection = None, bStrictErrorChecking = True):
    asbComponents = sbStatusLine.split(b" ", 2);
    if len(asbComponents) != 3:
      raise cHTTPInvalidMessageException(
        "The remote send an invalid status line.",
        o0Connection = o0Connection,
        dxDetails = {"sbStatusLine": sbStatusLine},
      );
    sbMethod, sbURL, sbVersion = asbComponents;
    if bStrictErrorChecking:
      dxDetails = {
        "sbStatusLine": sbStatusLine,
        "sbMethod": sbMethod,
        "sbURL": sbURL,
        "sbVersion": sbVersion,
      };
      if sbVersion not in [b"HTTP/1.0", b"HTTP/1.1"]:
        raise cHTTPInvalidMessageException(
          "The remote send an invalid HTTP version in the status line.",
          o0Connection = o0Connection,
          dxDetails = dxDetails,
        );
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    return {"sbzMethod": sbMethod, "sbURL": sbURL, "sbzVersion": sbVersion};
  
  @ShowDebugOutput
  def __init__(oSelf,
    sbURL,
    sbzMethod = zNotProvided,
    sbzVersion = zNotProvided,
    o0zHeaders = zNotProvided,
    sb0Body = None,
    s0Data = None,
    a0sbBodyChunks = None,
    o0AdditionalHeaders = None,
    bAutomaticallyAddContentLengthHeader = False
  ):
    fAssertType("sbURL", sbURL, bytes);
    fAssertType("sbzMethod", sbzMethod, bytes, zNotProvided);
    fAssertType("sbzVersion", sbzVersion, bytes, zNotProvided);
    fAssertType("o0zHeaders", o0zHeaders, cHTTPHeaders, None, zNotProvided);
    fAssertType("sb0Body", sb0Body, bytes, None);
    fAssertType("s0Data", s0Data, str, None);
    fAssertType("a0sbBodyChunks", a0sbBodyChunks, [bytes], None);
    fAssertType("o0AdditionalHeaders", o0AdditionalHeaders, cHTTPHeaders, None);
    oSelf.__sbURL = sbURL;
    oSelf.__sbMethod = fxGetFirstProvidedValue(sbzMethod, b"POST" if (sb0Body or s0Data or a0sbBodyChunks) else b"GET");
    iHTTPMessage.__init__(oSelf,
      sbzVersion,
      o0zHeaders,
      sb0Body,
      s0Data,
      a0sbBodyChunks,
      o0AdditionalHeaders,
      bAutomaticallyAddContentLengthHeader
    );
  
  @property
  def sbURL(oSelf):
    return oSelf.__sbURL;
  @sbURL.setter
  def sbURL(oSelf, sbURL):
    fAssertType("sbURL", sbURL, bytes);
    oSelf.__sbURL = sbURL;
  
  @property
  def sURLDecoded(oSelf):
    return urllib.parse.unquote(str(oSelf.__sbURL, "ascii", "strict"));
  @sURLDecoded.setter
  def sURLDecoded(oSelf, sURL):
    fAssertType("sURL", sURL, str);
    oSelf.__sbURL = bytes(urllib.parse.quote(sURL), "ascii", "strict");
  
  @property
  def sbMethod(oSelf):
    return oSelf.__sbMethod;
  @sbMethod.setter
  def sbMethod(oSelf, sbMethod):
    fAssertType("sbMethod", sbMethod, bytes);
    assert re.match("^[A-Z]+$", sbMethod), \
        "'sbMethod' must have one or more uppercase letters, not %s:%s" % (type(sbMethod), repr(sbMethod));
    oSelf.__sbMethod = sbMethod;
  
  @ShowDebugOutput
  def foClone(oSelf):
    if oSelf.bChunked:
      return cHTTPRequest(oSelf.sbURL, oSelf.sbMethod, oSelf.sbVersion, oSelf.oHeaders.foClone(), a0sbBodyChunks = oSelf.a0sbBodyChunks);
    return cHTTPRequest(oSelf.sbURL, oSelf.sbMethod, oSelf.sbVersion, oSelf.oHeaders.foClone(), sb0Body = oSelf.sb0Body);
  
  def fsbGetStatusLine(oSelf):
    return b"%s %s %s" % (oSelf.sbMethod, oSelf.sbURL, oSelf.sbVersion);
  
  @ShowDebugOutput
  def foCreateResponse(oSelf,
    sbzVersion = zNotProvided,
    uzStatusCode = zNotProvided,
    sbzReasonPhrase = zNotProvided,
    o0zHeaders = zNotProvided,
    sb0Body = None,
    s0Data = None,
    a0sbBodyChunks = None,
    sb0Charset = None,
    o0AdditionalHeaders = None,
    sb0MediaType = None,
    bAutomaticallyAddContentLengthHeader = False
  ):
    oResponse = cHTTPResponse(
      sbzVersion = fxGetFirstProvidedValue(sbzVersion, oSelf.sbVersion),
      uzStatusCode = uzStatusCode,
      sbzReasonPhrase = sbzReasonPhrase,
      o0zHeaders = o0zHeaders,
      sb0Body = sb0Body,
      s0Data = s0Data,
      a0sbBodyChunks = a0sbBodyChunks,
      o0AdditionalHeaders = o0AdditionalHeaders,
      bAutomaticallyAddContentLengthHeader = bAutomaticallyAddContentLengthHeader,
    );
    if sb0MediaType or sb0Body or s0Data or a0sbBodyChunks:
      oResponse.sb0MediaType = sb0MediaType if sb0MediaType is not None else b"application/octet-stream";
      if sb0Charset is not None:
        oResponse.sb0Charset = sb0Charset;
    else:
      assert sb0Charset is None, \
          "sb0Charset (%s) cannot be defined is sb0MediaType is None!" % repr(sb0Charset);
    return oResponse;
  
