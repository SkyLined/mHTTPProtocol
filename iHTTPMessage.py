import base64;

try: # mDebugOutput use is Optional
  from mDebugOutput import *;
except: # Do nothing if not available.
  ShowDebugOutput = lambda fxFunction: fxFunction;
  fShowDebugOutput = lambda sMessage: None;
  fEnableDebugOutputForModule = lambda mModule: None;
  fEnableDebugOutputForClass = lambda cClass: None;
  fEnableAllDebugOutput = lambda: None;
  cCallStack = fTerminateWithException = fTerminateWithConsoleOutput = None;

from mNotProvided import *;

from .cHTTPHeaders import cHTTPHeaders;
from .cURL import cURL;
from .fdsURLDecodedNameValuePairsFromString import fdsURLDecodedNameValuePairsFromString;
from .fsCompressData import fsCompressData;
from .fsDecompressData import fsDecompressData;
from .fsURLEncodedStringFromNameValuePairs import fsURLEncodedStringFromNameValuePairs;
from .mExceptions import *;

guBrotliCompressionQuality = 5;
guGZipCompressionLevel = 5;
guZLibCompressionLevel = 5;
guDeflateCompressionLevel = 5;

gbShowAllHeadersInStrReturnValue = False;

def fsASCII(s0Data, sDataTypeDescription):
  try:
    return str(s0Data or "");
  except:
    raise AssertionError("%s cannot contain Unicode characters: %s" % (sDataTypeDescription, repr(s0Data)));

class iHTTPMessage(object):
  sDefaultVersion = "HTTP/1.1";
  ddDefaultHeader_sValue_by_sName_by_sHTTPVersion = None;
  # A compression type is "supported" if this module can both compress and decompress data of that type.
  asSupportedCompressionTypes = list(set(fsCompressData.asSupportedCompressionTypes).intersection(fsDecompressData.asSupportedCompressionTypes));
  
  @classmethod
  @ShowDebugOutput
  def foParseHeaderLines(cClass, asHeaderLines):
    oHeaders = cHTTPHeaders();
    oMostRecentHeader = None;
    for sHeaderLine in asHeaderLines:
      if sHeaderLine[0] in " \t": # header continuation
        if oMostRecentHeader is None:
          raise cHTTPInvalidMessageException(
            "A header line continuation was sent on the first header line, which is not valid.",
            {"sHeaderLine": sHeaderLine},
          );
        oMostRecentHeader.fAddValueLine(sHeaderLine);
      else: # header
        asHeaderNameAndValue = sHeaderLine.split(":", 1);
        if len(asHeaderNameAndValue) != 2:
          raise cHTTPInvalidMessageException(
            "A header line did not contain a colon.",
            {"sHeaderLine": sHeaderLine},
          );
        oMostRecentHeader = oHeaders.foAddHeaderForNameAndValue(*asHeaderNameAndValue);
    return oHeaders;
  
  @ShowDebugOutput
  def __init__(oSelf,
    szVersion = zNotProvided,
    o0zHeaders = zNotProvided,
    s0Body = None,
    s0Data = None,
    a0sBodyChunks = None,
    o0AdditionalHeaders = None,
    bAutomaticallyAddContentLengthHeader = False
  ):
    assert s0Body is None or s0Data is None, \
          "Cannot provide both s0Body (%s) and s0Data (%s)!" % (repr(s0Body), repr(s0Data));
    assert s0Body is None or a0sBodyChunks is None, \
          "Cannot provide both s0Body (%s) and a0sBodyChunks (%s)!" % (repr(s0Body), repr(a0sBodyChunks));
    assert s0Data is None or a0sBodyChunks is None, \
          "Cannot provide both s0Data (%s) and a0sBodyChunks (%s)!" % (repr(s0Data), repr(a0sBodyChunks));
    oSelf.sVersion = fxGetFirstProvidedValue(szVersion, oSelf.sDefaultVersion);
    if fbIsProvided(o0zHeaders):
      oSelf.oHeaders = o0zHeaders or cHTTPHeaders();
    else:
      dDefaultHeader_sValue_by_sName = oSelf.ddDefaultHeader_sValue_by_sName_by_sHTTPVersion.get(oSelf.sVersion);
      assert dDefaultHeader_sValue_by_sName, \
          "Unsupported HTTP version %s" % repr(sVersion);
      oSelf.oHeaders = cHTTPHeaders.foFromDict(dDefaultHeader_sValue_by_sName);
    
    oSelf.o0AdditionalHeaders = o0AdditionalHeaders;
    oSelf.__s0Body = fsASCII(s0Body, "Body") if s0Body is not None else None;
    if s0Body is not None:
      o0ContentLengthHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Content-Length");
      if o0ContentLengthHeader is None:
        assert bAutomaticallyAddContentLengthHeader, \
            "Cannot provide s0Body (%s) without a \"Content-Length\" header or setting bAutomaticallyAddContentLengthHeader!" % repr(s0Body);
        oSelf.oHeaders.foAddHeaderForNameAndValue("Content-Length", str(len(oSelf.__s0Body)));
      else:
        assert long(o0ContentLengthHeader.sValue) == len(oSelf.__s0Body), \
            "Cannot provide %d bytes s0Body (%s) with a Content-Length: %s header!" % \
            (len(s0Body), repr(s0Body), o0ContentLengthHeader.sValue);
    bChunked = oSelf.oHeaders.fbHasUniqueValueForName("Transfer-Encoding", "Chunked");
    if a0sBodyChunks:
      assert bChunked, \
            "Cannot provide a0sBodyChunks (%s) without a \"Transfer-Encoded: Chunked\" header!" % repr(a0sBodyChunks);
      oSelf.__a0sBodyChunks = a0sBodyChunks[:];
    else:
      # If chunked encoding is enabled in the headers but no chunks are provided, default to an empty list.
      # Unless s0Data is provided; in that case the users is supplying the data for the body of the message directly.
      oSelf.__a0sBodyChunks = [] if bChunked and not s0Data else None;
    if s0Data is not None:
      oSelf.fSetData(s0Data);
  
  def __fSetContentTypeHeader(oSelf, s0ContentType, s0Charset, s0Boundary):
    if s0ContentType is None:
      # s0Charset and s0Boundary are ignored.
      oSelf.oHeaders.fbRemoveValue("Content-Type");
    else:
      assert isinstance(s0ContentType, (str, unicode)) and s0ContentType.strip() and "\r" not in s0ContentType and "\n" not in s0ContentType, \
          "s0ContentType must be None or a string that does contins at least one non-whitespace character and does not contain '\\r' or '\\n'";
      sContentTypeHeaderValue = s0ContentType;
      if s0Charset:
        assert isinstance(s0Charset, (str, unicode)) and s0Charset.strip() and "\r" not in s0Charset and "\n" not in s0Charset, \
            "s0Charset must be None or a string that does contins at least one non-whitespace character and does not contain '\\r' or '\\n'";
        sContentTypeHeaderValue += "; charset=" + str(s0Charset);
      if s0Boundary:
        assert isinstance(s0Boundary, (str, unicode)) and s0Boundary.strip() and "\r" not in s0Boundary and "\n" not in s0Boundary, \
            "s0Boundary must be None or a string that does contins at least one non-whitespace character and does not contain '\\r' or '\\n'";
        sContentTypeHeaderValue += "; boundary=" + str(s0Boundary);
      oSelf.oHeaders.fbReplaceHeadersForName("Content-Type", sContentTypeHeaderValue);
    if oSelf.o0AdditionalHeaders:
      oSelf.o0AdditionalHeaders.fbRemoveHeadersForName("Content-Type");
  
  @property
  def s0MediaType(oSelf):
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Content-Type");
    return o0ContentTypeHeader.sValue.split(";")[0].strip() if o0ContentTypeHeader else None;
  @s0MediaType.setter
  def s0MediaType(oSelf, s0Value):
    oSelf.__fSetContentTypeHeader(s0Value, oSelf.s0Charset, oSelf.s0Boundary);
  
  @property
  @ShowDebugOutput
  def s0Charset(oSelf):
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Content-Type");
    return o0ContentTypeHeader and o0ContentTypeHeader.fs0GetNamedValue("charset");
  @s0Charset.setter
  @ShowDebugOutput
  def s0Charset(oSelf, s0Value):
    oSelf.__fSetContentTypeHeader(oSelf.s0MediaType, s0Value, oSelf.s0Boundary);
  
  @property
  @ShowDebugOutput
  def s0Boundary(oSelf):
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Content-Type");
    return o0ContentTypeHeader and o0ContentTypeHeader.fs0GetNamedValue("boundary");
  @s0Boundary.setter
  @ShowDebugOutput
  def s0Boundary(oSelf, s0Value):
    oSelf.__fSetContentTypeHeader(oSelf.s0MediaType, oSelf.s0Charset, s0Value);
  
  @property
  @ShowDebugOutput
  def bChunked(oSelf):
    if oSelf.o0AdditionalHeaders:
      # The Transfer-Encoding is only valid in the first set of headers and not in any additional headers.
      aoTransferEncodingHeaders = oSelf.o0AdditionalHeaders.faoGetHeadersForName("Transfer-Encoding");
      if aoTransferEncodingHeaders:
        raise cHTTPInvalidMessageException(
          "Additional headers contain Transfer-Encoding headers",
          {"aoTransferEncodingHeaders": aoTransferEncodingHeaders},
        );
    return oSelf.oHeaders.fbHasUniqueValueForName("Transfer-Encoding", "Chunked");
  
  @property
  @ShowDebugOutput
  def bCloseConnection(oSelf):
    o0ConnectionHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Connection");
    if o0ConnectionHeader:
      if o0ConnectionHeader.sLowerName == "close":
        fShowDebugOutput("'Connection: Close' header found");
        return True;
      if o0ConnectionHeader.sLowerName == "keep-alive":
        fShowDebugOutput("'Connection: Keep-alive' header found");
        return False;
      # Any other values are ignored.
    # No valid Connection header found: return default, which depends on the HTTP version:
    if oSelf.sVersion.upper() == "HTTP/1.0":
      fShowDebugOutput("No 'Connection' header found; defaulting to 'Close' for %s" % oSelf.sVersion);
      return True;
    elif oSelf.sVersion.upper() == "HTTP/1.1":
      fShowDebugOutput("No 'Connection' header found; defaulting to 'Keep-alive' for %s" % oSelf.sVersion);
      return False;
    raise cHTTPInvalidMessageException(
      "Invalid HTTP version!",
      {"sHTTPVersion": oSelf.sVersion},
    );
  
  @property
  @ShowDebugOutput
  def bCompressed(oSelf):
    for sCompressionType in oSelf.asCompressionTypes or []:
      if sCompressionType.lower() != "identity":
        return True;
    return False;
  
  @property
  @ShowDebugOutput
  def asCompressionTypes(oSelf):
    o0ContentEncodingHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Content-Encoding");
    return [s.strip() for s in o0ContentEncodingHeader.sValue.split(",")] if o0ContentEncodingHeader else [];
  
  @property
  def s0Data(oSelf):
    # Returns decoded and decompressed body based on the Content-Encoding header.
    s0Data = oSelf.__s0Body if not oSelf.bChunked else "".join(oSelf.__a0sBodyChunks);
    if s0Data is None:
      return None;
    sData = s0Data; # Never None past this point.
    for sCompressionType in reversed(oSelf.asCompressionTypes):
      sData = fsDecompressData(sData, sCompressionType);
    s0Charset = oSelf.s0Charset;
    if s0Charset is not None:
      # Convert bytes to unicode using charset defined in Content-Type header.
      sData = unicode(sData, s0Charset, "replace");
    return sData;
  
  @ShowDebugOutput
  def fSetData(oSelf, sData, bCloseConnectionInsteadOfUsingContentLength = False):
    s0Charset = oSelf.s0Charset;
    if isinstance(s0Charset, unicode):
      # Convert unicode to bytes using charset defined in Content-Type header.
      sData = str(sData, s0Charset);
    else:
      assert isinstance(sData, str), \
          "sData (%s) must be an byte string or a uncideo string (provided the s0Charset property is set to allow conversion to a byte string)";
    # Sets the (optionally) compressed body of the message.
    for sCompressionType in reversed(oSelf.asCompressionTypes):
      sData = fsCompressData(sData, sCompressionType);
    oSelf.fSetBody(sData, bCloseConnectionInsteadOfUsingContentLength);
  
  @property
  @ShowDebugOutput
  def sBody(oSelf):
    if not oSelf.bChunked:
      return oSelf.__s0Body;
    assert not oSelf.bChunked or oSelf.__a0sBodyChunks is not None, \
        "wtf!?";
    return "".join([
      "%X\r\n%s\r\n" % (len(sBodyChunk), sBodyChunk) 
      for sBodyChunk in oSelf.__a0sBodyChunks
    ]) + "0\r\n\r\n";
  
  @ShowDebugOutput
  def fSetBody(oSelf, sBody, bCloseConnectionInsteadOfUsingContentLength = False):
    oSelf.oHeaders.fbRemoveHeadersForName("Transfer-Encoding");
    if oSelf.sVersion.upper() != "HTTP/1.1":
      bCloseConnectionInsteadOfUsingContentLength = True;
    if bCloseConnectionInsteadOfUsingContentLength:
      oSelf.oHeaders.fbReplaceHeadersForName("Connection", "Close");
      oSelf.oHeaders.fbRemoveHeadersForName("Content-Length");
    else:
      oSelf.oHeaders.fbReplaceHeadersForName("Content-Length", str(len(sBody)));
    oSelf.__s0Body = fsASCII(sBody, "Body");
    oSelf.__a0sBodyChunks = None;
  
  @property
  @ShowDebugOutput
  def asBodyChunks(oSelf):
    assert oSelf.bChunked, \
        "Cannot get body chunks when chunked encoding is not enabled";
    return oSelf.__a0sBodyChunks[:];
  
  @ShowDebugOutput
  def fSetBodyChunks(oSelf, asBodyChunks):
    for sBodyChunk in asBodyChunks:
      assert sBodyChunk, \
          "Cannot add empty body chunks";
    oSelf.oHeaders.fbRemoveHeadersForName("Content-Length");
    oSelf.oHeaders.fbReplaceHeadersForName("Transfer-Encoding", "Chunked");
    oSelf.__s0Body = None;
    oSelf.__a0sBodyChunks = asBodyChunks[:];
  
  @ShowDebugOutput
  def fAddBodyChunk(oSelf, sBodyChunk):
    assert sBodyChunk, \
        "Cannot add an empty chunk!"
    assert oSelf.__s0Body is None, \
        "Cannot add a chunk if body is set";
    if not oSelf.bChunked:
      oSelf.fSetBodyChunks([sBodyChunk]);
    else:
      oSelf.__a0sBodyChunks.append(sBodyChunk);
  
  @ShowDebugOutput
  def fRemoveBody(oSelf):
    oSelf.oHeaders.fbRemoveHeadersForName("Content-Encoding");
    oSelf.oHeaders.fbRemoveHeadersForName("Content-Length");
    oSelf.oHeaders.fbRemoveHeadersForName("Transfer-Encoding", "Chunked");
    oSelf.__s0Body = None;
    oSelf.__a0sBodyChunks = None;
  
  # application/x-www-form-urlencoded
  @property
  @ShowDebugOutput
  def d0Form_sValue_by_sName(oSelf):
    # convert the decoded and decompressed body to form name-value pairs.
    s0MediaType = oSelf.s0MediaType;
    if s0MediaType is None or s0MediaType.lower() != "application/x-www-form-urlencoded":
      return None;
    s0Data = oSelf.s0Data;
    return fdsURLDecodedNameValuePairsFromString(s0Data) if s0Data else {};
  
  @ShowDebugOutput
  def fs0GetFormValue(oSelf, sName):
    # convert the decoded and decompressed body to form name-value pairs and return the value for the given name
    # or None if there is no such value.
    d0Form_sValue_by_sName = oSelf.d0Form_sValue_by_sName;
    assert d0Form_sValue_by_sName, \
        "HTTP Message does not contain URL encoded form data.";
    dForm_sValue_by_sName = d0Form_sValue_by_sName;
    sLowerCaseName = sName.lower();
    for (sName, sValue) in dForm_sValue_by_sName.items():
      if sLowerCaseName == sName.lower():
        return sValue;
    return None;
  
  @ShowDebugOutput
  def fSetFormValue(oSelf, sName, s0Value):
    # Convert the decoded and decompressed body to form name-value pairs,
    # remove all existing values with the given name,
    # if the value is not None, add the new named value,
    # and update the optionally compressed body to match.
    sLowerStrippedName = sName.strip().lower();
    d0Form_sValue_by_sName = oSelf.d0Form_sValue_by_sName;
    assert d0Form_sValue_by_sName, \
        "HTTP Message does not contain URL encoded form data.";
    dForm_sValue_by_sName = d0Form_sValue_by_sName;
    for sOtherName in dForm_sValue_by_sName.keys():
      if sLowerStrippedName == sOtherName.lower():
        del dForm_sValue_by_sName[sOtherName];
    if s0Value is not None:
      dForm_sValue_by_sName[sName] = s0Value;
    oSelf.fSetData(fsURLEncodedStringFromNameValuePairs(dForm_sValue_by_sName));
  
  @ShowDebugOutput
  def fRemoveFormValue(oSelf, sName):
    oSelf.fSetFormValue(sName, None);
  
  # Authorization
  @ShowDebugOutput
  def ftszGetBasicAuthorization(oSelf):
    s0Authorization = oSelf.oHeaders.fs0GetUniqueHeaderValue("Authorization");
    if s0Authorization is None:
      return (None, None);
    sBasic, sBase64EncodedUserNameColonPassword = s0Authorization.strip().split(" ", 1);
    if sBasic.lower() != "basic ":
      return (None, None);
    try:
      sUserNameColonPassword = base64.b64decode(sBase64EncodedUserNameColonPassword.lstrip());
    except Exception as oException:
      return (None, None);
    if ":" in sUserNameColonPassword:
      sUserName, sPassword = sUserNameColonPassword.split(":", 1);
    else:
      sUserName = sUserNameColonPassword;
      sPassword = None;
    return (sUserName, sPassword);

  @ShowDebugOutput
  def fSetBasicAuthorization(oSelf, sUserName, sPassword):
    sBase64EncodedUserNameColonPassword = base64.b64encode("%s:%s" % (sUserName, sPassword));
    oSelf.oHeaders.fbReplaceHeadersForName("Authorization", "basic %s" % sBase64EncodedUserNameColonPassword);
  
  def fsSerialize(oSelf):
    return "\r\n".join([
      oSelf.fsGetStatusLine(),
    ] + oSelf.oHeaders.fasGetHeaderLines() + [
      "",
      oSelf.sBody or "",
    ]);
  
  def fasGetDetails(oSelf):
    # Make sure not to call *any* method that has ShowDebugOutput, as this causes
    # fasGetDetails to get called again, resulting in infinite recursion.
    if oSelf.oHeaders.fbHasUniqueValueForName("Transfer-Encoding", "Chunked"):
      asChunks = oSelf.__a0sBodyChunks;
      sBodyDetails = "%d bytes body in %d chunks" % (sum([len(sChunk) for sChunk in asChunks]), len(asChunks));
    else:
      s0Body = oSelf.__s0Body;
      sBodyDetails = "%d bytes body" % len(s0Body) if s0Body is not None else "no body";
    
    o0ContentEncodingHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Content-Encoding", oSelf.o0AdditionalHeaders);
    sCompressionTypes = ">".join([s.strip() for s in o0ContentEncodingHeader.sValue.split(",")]) if o0ContentEncodingHeader else None;
    
    bCloseConnection = oSelf.oHeaders.fbHasUniqueValueForName("Connection", "Close");
    
    o0HostHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Host", oSelf.o0AdditionalHeaders);
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName("Content-Type", oSelf.o0AdditionalHeaders);
    s0MediaType = o0ContentTypeHeader.sValue.split(";")[0].strip() if o0ContentTypeHeader else None;
    return [s for s in [
      oSelf.fsGetStatusLine(),
      "%d headers" % oSelf.oHeaders.uNumberOfHeaders if not gbShowAllHeadersInStrReturnValue else None,
      "Host: %s" % o0HostHeader.sValue if o0HostHeader and not gbShowAllHeadersInStrReturnValue else None,
    ] if s] + (
      [
        "%s: %s" % (oHeader.sName, oHeader.sValue)
        for oHeader in oSelf.oHeaders.faoGetHeaders()
      ] if gbShowAllHeadersInStrReturnValue else []
    ) + [s for s in [
      s0MediaType,
      sBodyDetails,
      "%s compressed" % sCompressionTypes if sCompressionTypes else None,
      "%d additional headers" % oSelf.o0AdditionalHeaders.uNumberOfHeaders if oSelf.o0AdditionalHeaders else None,
      "close connection" if bCloseConnection else "",
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));

