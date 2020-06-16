import base64, zlib;
try:
  from .cBrotli import cBrotli;
except Exception:
  cBrotli = None;
from .cInvalidMessageException import cInvalidMessageException;
from .cHTTPHeaders import cHTTPHeaders;
from .cURL import cURL;
from .fsURLEncodedStringFromNameValuePairs import fsURLEncodedStringFromNameValuePairs;
from .fdsURLDecodedNameValuePairsFromString import fdsURLDecodedNameValuePairsFromString;

from mDebugOutput import ShowDebugOutput, fShowDebugOutput;

guBrotliCompressionQuality = 5;
guGZipCompressionLevel = 5;
guZLibCompressionLevel = 5;
guDeflateCompressionLevel = 5;

def fsASCII(sData, sDataTypeDescription):
  try:
    return str(sData or "");
  except:
    raise AssertionError("%s cannot contain Unicode characters: %s" % (sDataTypeDescription, repr(sData)));

class iHTTPMessage(object):
  cInvalidMessageException = cInvalidMessageException;
  cHTTPHeaders = cHTTPHeaders;
  asSupportedCompressionTypes = ["deflate", "gzip", "x-gzip", "zlib"] + (["br"] if cBrotli else []);
  
# Deprecated functions and their equivalent existing function:
#  foHeadersFromDict => cHTTPHeaders.foFromDict
#  fszHeadersGetLastNamedValueForUniqueValue => oHeader.fszGetNamedValue
#  fozGetUniqueHeader => fozHeadersGetUnique
#  fbHasUniqueHeaderValue => fbHeadersHaveUniqueValue
#  fszGetUniqueHeaderNamedValue => oHeader.fszGetNamedValue
  
  @classmethod
  @ShowDebugOutput
  def foParseHeaderLines(cClass, asHeaderLines):
    oHeaders = cHTTPHeaders();
    oMostRecentHeader = None;
    for sHeaderLine in asHeaderLines:
      if sHeaderLine[0] in " \t": # header continuation
        if oMostRecentHeader is None:
          raise cInvalidMessageException(
            "A header line continuation was sent on the first header line, which is not valid.",
            {"sHeaderLine": sHeaderLine},
          );
        oMostRecentHeader.fAddValueLine(sHeaderLine);
      else: # header
        asHeaderNameAndValue = sHeaderLine.split(":", 1);
        if len(asHeaderNameAndValue) != 2:
          raise cInvalidMessageException(
            "A header line did not contain a colon.",
            {"sHeaderLine": sHeaderLine},
          );
        oMostRecentHeader = oHeaders.foAddHeaderForNameAndValue(*asHeaderNameAndValue);
    return oHeaders;
  
  @ShowDebugOutput
  def fozHeadersGetUnique(oSelf, sName):
    return oSelf.oHeaders.fozGetUniqueHeaderForName(sName, oSelf.ozAdditionalHeaders);
  @ShowDebugOutput
  def fbHeadersHaveUniqueValue(oSelf, sName, sValue):
    return oSelf.oHeaders.fbHasUniqueValueForName(sName, sValue, oSelf.ozAdditionalHeaders);
  
  @ShowDebugOutput
  def __init__(oSelf, szVersion = None, ozHeaders = None, szBody = None, szData = None, azsBodyChunks = None, ozAdditionalHeaders = None):
    assert szBody is None or szData is None, \
          "Cannot provide both sBody (%s) and sData (%s)!" % (repr(szBody), repr(szData));
    assert szBody is None or azsBodyChunks is None, \
          "Cannot provide both sBody (%s) and asBodyChunks (%s)!" % (repr(szBody), repr(azsBodyChunks));
    assert szData is None or azsBodyChunks is None, \
          "Cannot provide both sData (%s) and asBodyChunks (%s)!" % (repr(szData), repr(azsBodyChunks));
    oSelf.sVersion = szVersion if szVersion else "HTTP/1.1";
    oSelf.oHeaders = ozHeaders or cHTTPHeaders.foDefaultHeadersForVersion(oSelf.sVersion);
    oSelf.__szBody = None;
    oSelf.__azsBodyChunks = None;
    oSelf.ozAdditionalHeaders = ozAdditionalHeaders;
    if szBody is not None:
      oSelf.fSetBody(szBody);
    elif szData is not None:
      oSelf.fSetData(szData);
    elif azsBodyChunks is not None:
      oSelf.fSetBodyChunks(azsBodyChunks);
    if oSelf.bChunked:
      assert oSelf.__azsBodyChunks is not None, \
          "Missing asBodyChunks!?";
    else:
      assert oSelf.__azsBodyChunks is None, \
          "Unexpected asBodyChunks";
  
  @property
  @ShowDebugOutput
  def szMediaType(oSelf):
    ozContentTypeHeader = oSelf.fozHeadersGetUnique("Content-Type");
    return ozContentTypeHeader.sValue.split(";")[0].strip() if ozContentTypeHeader else None;
  
  @szMediaType.setter
  @ShowDebugOutput
  def szMediaType(oSelf, szValue):
    if szValue is None:
      oSelf.oHeaders.fbRemoveValue("Content-Type");
    else:
      sContentType = szValue;
      szCharset = oSelf.szCharset;
      if szCharset:
        sContentType += "; charset=" + szCharset;
      szBoundary = oSelf.szBoundary;
      if szBoundary:
        sContentType += "; boundary=" + szBoundary;
      oSelf.oHeaders.foAddHeaderForNameAndValue("Content-Type", sContentType);
  
  @property
  @ShowDebugOutput
  def szCharset(oSelf):
    ozContentTypeHeader = oSelf.fozHeadersGetUnique("Content-Type");
    return ozContentTypeHeader and ozContentTypeHeader.fszGetNamedValue("charset");
  @szCharset.setter
  @ShowDebugOutput
  def szCharset(oSelf, szValue):
    sContentType = oSelf.szMediaType;
    assert sContentType is not None, \
        "Cannot set a charset without a media type!";
    if szValue is not None:
      sContentType += "; charset=" + szValue;
    szBoundary = oSelf.szBoundary;
    if szBoundary:
      sContentType += "; boundary=" + szBoundary;
    oSelf.oHeaders.foAddHeaderForNameAndValue("Content-Type", sContentType);
    if oSelf.ozAdditionalHeaders:
      oSelf.ozAdditionalHeaders.fbRemoveValue("Content-Type");
  
  @property
  @ShowDebugOutput
  def sBoundary(oSelf):
    ozContentTypeHeader = oSelf.fozHeadersGetUnique("Content-Type");
    return ozContentTypeHeader and ozContentTypeHeader.fszGetNamedValue("boundary");
  @sBoundary.setter
  @ShowDebugOutput
  def sBoundary(oSelf, sValue):
    sContentType = oSelf.sMediaType;
    assert sContentType is not None, \
        "Cannot set a boundary without a media type!";
    szCharset = oSelf.szCharset;
    if szCharset is not None:
      sContentType += "; charset=" + szCharset;
    sContentType += "; boundary=" + sValue;
    oSelf.oHeaders.foAddHeaderForNameAndValue("Content-Type", sContentType);
  
  @property
  @ShowDebugOutput
  def bChunked(oSelf):
    # The Transfer-Encoding is only valid in the first set of headers and not in any additional headers.
    if oSelf.ozAdditionalHeaders:
      aoTransferEncodingHeaders = oSelf.ozAdditionalHeaders.faoGetHeadersForName("Transfer-Encoding");
      if aoTransferEncodingHeaders:
        raise cInvalidMessageException(
          "Additional headers contain Transfer-Encoding headers",
          {"aoTransferEncodingHeaders": aoTransferEncodingHeaders},
        );
    return oSelf.oHeaders.fbHasUniqueValueForName("Transfer-Encoding", "Chunked");

  @property
  @ShowDebugOutput
  def bCloseConnection(oSelf):
    ozConnectionHeader = oSelf.fozHeadersGetUnique("Connection");
    if ozConnectionHeader:
      if ozConnectionHeader.sLowerName == "close":
        fShowDebugOutput("'Connection: Close' header found");
        return True;
      if ozConnectionHeader.sLowerName == "keep-alive":
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
    raise cInvalidMessageException(
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
    ozContentEncodingHeader = oSelf.fozHeadersGetUnique("Content-Encoding");
    return [s.strip() for s in ozContentEncodingHeader.sValue.split(",")] if ozContentEncodingHeader else [];
  
  @property
  def sData(oSelf):
    # Returns decoded and decompressed body based on the Content-Encoding header.
    sData = oSelf.__szBody if not oSelf.bChunked else "".join(oSelf.__azsBodyChunks);
    if sData is None:
      return None;
    asCompressionTypes = oSelf.asCompressionTypes;
    if len(asCompressionTypes) > 0:
      for sCompressionType in reversed(asCompressionTypes):
        sLowerCompressionType = sCompressionType.lower();
        if cBrotli and sLowerCompressionType == "br":
          oBrotli = cBrotli();
          sData = oBrotli.decompress(sData) + oBrotli.flush();
        elif sLowerCompressionType == "deflate":
          sData = zlib.decompress(sData, -zlib.MAX_WBITS);
        elif sLowerCompressionType in ["gzip", "x-gzip"]:
          sData = zlib.decompress(sData, zlib.MAX_WBITS | 0x10);
        elif sLowerCompressionType == "identity":
          pass; # No compression.
        elif sLowerCompressionType == "zlib":
          sData = zlib.decompress(sData, zlib.MAX_WBITS);
        else:
          raise NotImplementedError("Content encoding %s is not supported" % sEncodingType);
    szCharset = oSelf.szCharset;
    if szCharset is not None:
      # Convert bytes to unicode using charset defined in Content-Type header.
      sData = unicode(sData, szCharset, "replace");
    return sData;

  @ShowDebugOutput
  def fSetData(oSelf, sData, bCloseConnectionInsteadOfUsingContentLength = False):
    szCharset = oSelf.szCharset;
    if szCharset is not None:
      # Convert unicode to bytes using charset defined in Content-Type header.
      sData = str(sData, szCharset);
    # Sets the (optionally) compressed body of the message.
    asCompressionTypes = oSelf.asCompressionTypes;
    if len(asCompressionTypes) > 0:
      for sCompressionType in reversed(asCompressionTypes):
        sLowerCompressionType = sCompressionType.lower();
        if cBrotli and sLowerCompressionType == "br":
          sData = cBrotli().compress(sData, guBrotliCompressionQuality);
        elif sLowerCompressionType == "deflate":
          oCompressionObject = zlib.compressobj(guDeflateCompressionLevel, zlib.DEFLATED, -zlib.MAX_WBITS);
          sData = oCompressionObject.compress(sData) + oCompressionObject.flush();
        elif sLowerCompressionType in ["gzip", "x-gzip"]:
          oCompressionObject = zlib.compressobj(guGZipCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS | 0x10);
          sData = oCompressionObject.compress(sData) + oCompressionObject.flush();
        elif sLowerCompressionType == "identity":
          pass; # No compression.
        elif sLowerCompressionType == "zlib":
          oCompressionObject = zlib.compressobj(guZLibCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS);
          sData = oCompressionObject.compress(sData) + oCompressionObject.flush();
        else:
          raise NotImplementedError("Content encoding %s is not supported" % sEncodingType);
    oSelf.fSetBody(sData, bCloseConnectionInsteadOfUsingContentLength);

  @property
  @ShowDebugOutput
  def sBody(oSelf):
    if not oSelf.bChunked:
      return oSelf.__szBody;
    assert not oSelf.bChunked or oSelf.__azsBodyChunks is not None, \
        "wtf!?";
    return "".join([
      "%X\r\n%s\r\n" % (len(sBodyChunk), sBodyChunk) 
      for sBodyChunk in oSelf.__azsBodyChunks
    ]) + "0\r\n\r\n";
  
  @ShowDebugOutput
  def fSetBody(oSelf, sBody, bCloseConnectionInsteadOfUsingContentLength = False):
    oSelf.oHeaders.fbRemoveHeadersForName("Transfer-Encoding");
    if oSelf.sVersion.upper() != "HTTP/1.1":
      bCloseConnectionInsteadOfUsingContentLength = True;
    if bCloseConnectionInsteadOfUsingContentLength:
      oSelf.oHeaders.foAddHeaderForNameAndValue("Connection", "Close");
      oSelf.oHeaders.fbRemoveHeadersForName("Content-Length");
    else:
      oSelf.oHeaders.foAddHeaderForNameAndValue("Content-Length", str(len(sBody)));
    oSelf.__szBody = fsASCII(sBody, "Body");
    oSelf.__azsBodyChunks = None;

  @property
  @ShowDebugOutput
  def asBodyChunks(oSelf):
    assert oSelf.bChunked, \
        "Cannot get body chunks when chunked encoding is not enabled";
    return oSelf.__azsBodyChunks[:];
  
  @ShowDebugOutput
  def fSetBodyChunks(oSelf, asBodyChunks):
    for sBodyChunk in asBodyChunks:
      assert sBodyChunk, \
          "Cannot add empty body chunks";
    oSelf.oHeaders.fbRemoveHeadersForName("Content-Length");
    oSelf.oHeaders.foAddHeaderForNameAndValue("Transfer-Encoding", "Chunked");
    oSelf.__szBody = None;
    oSelf.__azsBodyChunks = asBodyChunks[:];
  
  @ShowDebugOutput
  def fAddBodyChunk(oSelf, sBodyChunk):
    assert sBodyChunk, \
        "Cannot add an empty chunk!"
    assert oSelf.__szBody is None, \
        "Cannot add a chunk if body is set";
    if not oSelf.bChunked:
      oSelf.fSetBodyChunks([sBodyChunk]);
    else:
      oSelf.__azsBodyChunks.append(sBodyChunk);
  
  @ShowDebugOutput
  def fRemoveBody(oSelf):
    oSelf.oHeaders.fbRemoveHeadersForName("Content-Encoding");
    oSelf.oHeaders.fbRemoveHeadersForName("Content-Length");
    oSelf.oHeaders.fbRemoveHeadersForName("Transfer-Encoding", "Chunked");
    oSelf.__szBody = None;
    oSelf.__azsBodyChunks = None;
  
  # application/x-www-form-urlencoded
  @property
  @ShowDebugOutput
  def dzForm_sValue_by_sName(oSelf):
    # convert the decoded and decompressed body to form name-value pairs.
    szMediaType = oSelf.szMediaType;
    if szMediaType is None or szMediaType.lower() != "application/x-www-form-urlencoded":
      return None;
    return fdsURLDecodedNameValuePairsFromString(oSelf.sData);
  
  @ShowDebugOutput
  def fszGetFormValue(oSelf, sName):
    # convert the decoded and decompressed body to form name-value pairs and return the value for the given name
    # or None if there is no such value.
    sLowerCaseName = sName.lower();
    for (sName, sValue) in oSelf.dForm_sValue_by_sName.items():
      if sLowerCaseName == sName.lower():
        return sValue;
    return None;
  
  @ShowDebugOutput
  def fSetFormValue(oSelf, sName, sValue):
    # convert the decoded and decompressed body to form name-value pairs, set the given name to the given value 
    # and update the optionally compressed body to match.
    sLowerStrippedName = sName.strip().lower();
    dForm_sValue_by_sName = oSelf.dForm_sValue_by_sName;
    for sOtherName in dForm_sValue_by_sName.keys():
      if sLowerStrippedName == sOtherName.lower():
        del dForm_sValue_by_sName[sOtherName];
    dForm_sValue_by_sName[sName] = sValue;
    oSelf.sData = fsURLEncodedStringFromNameValuePairs(dForm_sValue_by_sName);
  
  # Authorization
  @ShowDebugOutput
  def ftszGetBasicAuthorization(oSelf):
    szAuthorization = oSelf.oHeaders.fszGetUniqueHeaderValue("Authorization");
    if szAuthorization is None:
      return (None, None);
    sBasic, sBase64EncodedUserNameColonPassword = szAuthorization.strip().split(" ", 1);
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
    oSelf.oHeaders.foAddHeaderForNameAndValue("Authorization", "basic %s" % sBase64EncodedUserNameColonPassword);
  
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
      asChunks = oSelf.__azsBodyChunks;
      sBodyDetails = "%d bytes body in %d chunks" % (sum([len(sChunk) for sChunk in asChunks]), len(asChunks));
    else:
      szBody = oSelf.__szBody;
      sBodyDetails = "%d bytes body" % len(szBody) if szBody is not None else "no body";
    
    ozContentEncodingHeader = oSelf.oHeaders.fozGetUniqueHeaderForName("Content-Encoding", oSelf.ozAdditionalHeaders);
    sCompressionTypes = ">".join([s.strip() for s in ozContentEncodingHeader.sValue.split(",")]) if ozContentEncodingHeader else None;
    
    bCloseConnection = oSelf.oHeaders.fbHasUniqueValueForName("Connection", "Close");
    
    ozContentTypeHeader = oSelf.oHeaders.fozGetUniqueHeaderForName("Content-Type", oSelf.ozAdditionalHeaders);
    szMediaType = ozContentTypeHeader.sValue.split(";")[0].strip() if ozContentTypeHeader else None;
    return [s for s in [
      oSelf.fsGetStatusLine(),
      "%d headers" % oSelf.oHeaders.uNumberOfHeaders,
      szMediaType,
      sBodyDetails,
      "%s compressed" % sCompressionTypes if sCompressionTypes else None,
      "%d additional headers" % oSelf.ozAdditionalHeaders.uNumberOfHeaders if oSelf.ozAdditionalHeaders else None,
      "close connection" if bCloseConnection else "",
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));
