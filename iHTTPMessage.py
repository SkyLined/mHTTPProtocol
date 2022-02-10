import base64;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

from mNotProvided import *;

from .cHTTPHeaders import cHTTPHeaders;
from .cURL import cURL;
from .fdsURLDecodedNameValuePairsFromString import fdsURLDecodedNameValuePairsFromString;
from .fsbCompressData import fsbCompressData;
from .fsbDecompressData import fsbDecompressData;
from .fsbURLEncodedNameValuePairsToBytesString import fsbURLEncodedNameValuePairsToBytesString;
from .mExceptions import *;

guBrotliCompressionQuality = 5;
guGZipCompressionLevel = 5;
guZLibCompressionLevel = 5;
guDeflateCompressionLevel = 5;

gbShowAllHeadersInStrReturnValue = False;

class iHTTPMessage(object):
  sbDefaultVersion = b"HTTP/1.1";
  ddDefaultHeader_sbValue_by_sbName_by_sbHTTPVersion = None;
  # A compression type is "supported" if this module can both compress and decompress data of that type.
  asbSupportedCompressionTypes = list(set(fsbCompressData.asbSupportedCompressionTypes).intersection(fsbDecompressData.asbSupportedCompressionTypes));
  
  @classmethod
  @ShowDebugOutput
  def foParseHeaderLines(cClass, asbHeaderLines, o0Connection = None, bStrictErrorChecking = True):
    oHeaders = cHTTPHeaders();
    oMostRecentHeader = None;
    for sbHeaderLine in asbHeaderLines:
      if sbHeaderLine[0] in b" \t": # header continuation
        if oMostRecentHeader is not None:
          oMostRecentHeader.fAddValueLine(sbHeaderLine);
        elif bStrictErrorChecking:
          raise cHTTPInvalidMessageException(
            "A header line continuation was sent on the first header line, which is not valid.",
            o0Connection = o0Connection,
            dxDetails = {"sbHeaderLine": sbHeaderLine},
          );
      else: # header
        tsbHeaderNameAndValue = sbHeaderLine.split(b":", 1);
        if len(tsbHeaderNameAndValue) == 2:
          oMostRecentHeader = oHeaders.foAddHeaderForNameAndValue(*tsbHeaderNameAndValue);
        elif bStrictErrorChecking:
          raise cHTTPInvalidMessageException(
            "A header line did not contain a colon.",
            o0Connection = o0Connection,
            dxDetails = {"sbHeaderLine": sbHeaderLine},
          );
    return oHeaders;
  
  @ShowDebugOutput
  def __init__(oSelf,
    sbzVersion = zNotProvided,
    o0zHeaders = zNotProvided,
    sb0Body = None,
    s0Data = None,
    a0sbBodyChunks = None,
    o0AdditionalHeaders = None,
    bAutomaticallyAddContentLengthHeader = False
  ):
    fAssertType("sbzVersion", sbzVersion, bytes, zNotProvided);
    fAssertType("o0zHeaders", o0zHeaders, cHTTPHeaders, None, zNotProvided); # None means no headers.
    fAssertType("sb0Body", sb0Body, bytes, None);
    fAssertType("s0Data", s0Data, str, None);
    fAssertType("a0sbBodyChunks", a0sbBodyChunks, [bytes], None);
    fAssertType("o0AdditionalHeaders", o0AdditionalHeaders, cHTTPHeaders, None); # None means no additional headers.
    assert sb0Body is None or s0Data is None, \
          "Cannot provide both sb0Body (%s) and s0Data (%s)!" % (repr(sb0Body), repr(s0Data));
    assert sb0Body is None or a0sbBodyChunks is None, \
          "Cannot provide both sb0Body (%s) and a0sbBodyChunks (%s)!" % (repr(sb0Body), repr(a0sbBodyChunks));
    assert s0Data is None or a0sbBodyChunks is None, \
          "Cannot provide both s0Data (%s) and a0sbBodyChunks (%s)!" % (repr(s0Data), repr(a0sbBodyChunks));
    
    oSelf.sbVersion = fxGetFirstProvidedValue(sbzVersion, oSelf.sbDefaultVersion);
    
    if fbIsProvided(o0zHeaders):
      oSelf.oHeaders = o0zHeaders or cHTTPHeaders();
    else:
      dDefaultHeader_sbValue_by_sbName = oSelf.ddDefaultHeader_sbValue_by_sbName_by_sbHTTPVersion.get(oSelf.sbVersion);
      assert dDefaultHeader_sbValue_by_sbName, \
          "Unsupported HTTP version %s" % repr(oSelf.sbVersion);
      oSelf.oHeaders = cHTTPHeaders.foFromDict(dDefaultHeader_sbValue_by_sbName);
    
    bConnectionCloseHeaderPresent = oSelf.oHeaders.fbHasUniqueValueForName(b"Connection", b"Close");
    o0ContentLengthHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Length");
    bChunked = oSelf.oHeaders.fbHasUniqueValueForName(b"Transfer-Encoding", b"Chunked");
    if sb0Body is not None:
      assert not bChunked, \
            "Cannot provide sb0Body (%s) with a \"Transfer-Encoded: Chunked\" header!" % repr(sb0Body);
      oSelf.__sb0Body = sb0Body;
      oSelf.__a0sbBodyChunks = None;
      o0ContentLengthHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Length");
      if o0ContentLengthHeader is None:
        assert bConnectionCloseHeaderPresent or bAutomaticallyAddContentLengthHeader, \
            "Cannot provide sb0Body (%s) without a \"Content-Length\" header or setting bAutomaticallyAddContentLengthHeader!" % repr(sb0Body);
        oSelf.oHeaders.foAddHeaderForNameAndValue(b"Content-Length", b"%d" % len(sb0Body));
      else:
        assert int(o0ContentLengthHeader.sbValue) == len(oSelf.__sb0Body), \
            "Cannot provide %d bytes sb0Body (%s) with a Content-Length: %s header!" % \
            (len(sb0Body), repr(sb0Body), repr(o0ContentLengthHeader.sbValue));
    else:
      assert o0ContentLengthHeader is None, \
          "Cannot have a %s header without a body" % repr(o0ContentLengthHeader.sbValue);
      oSelf.__sb0Body = None;
      if a0sbBodyChunks:
        assert bChunked, \
              "Cannot provide a0sbBodyChunks (%s) without a \"Transfer-Encoded: Chunked\" header!" % repr(a0sbBodyChunks);
        oSelf.__a0sbBodyChunks = a0sbBodyChunks[:];
      elif s0Data is None:
        if bChunked:
          # If chunked encoding is enabled in the headers but no chunks or data is provided: default to an empty list.
          oSelf.__a0sbBodyChunks = [];
      else:
        oSelf.fSetData(s0Data);
        
    oSelf.o0AdditionalHeaders = o0AdditionalHeaders;
  
  def __fSetContentTypeHeader(oSelf, sb0ContentType, sb0Charset, sb0Boundary):
    fAssertType("sb0ContentType", sb0ContentType, bytes, None);
    fAssertType("sb0Charset", sb0Charset, bytes, None);
    fAssertType("sb0Boundary", sb0Boundary, bytes, None);
    if sb0ContentType is None:
      # s0Charset and s0Boundary are ignored.
      oSelf.oHeaders.fbRemoveValue(b"Content-Type");
    else:
      assert b"\r" not in sb0ContentType and b"\n" not in sb0ContentType and sb0ContentType.strip(), \
          "sb0ContentType must be None or a 'bytes' that does contins at least one non-whitespace character and does not contain '\\r' or '\\n'";
      sbContentTypeHeaderValue = sb0ContentType;
      if sb0Charset:
        assert b"\r" not in sb0Charset and b"\n" not in sb0Charset and sb0Charset.strip(), \
            "sb0Charset must be None or a string that does contins at least one non-whitespace character and does not contain '\\r' or '\\n'";
        sbContentTypeHeaderValue += b"; charset=" + sb0Charset;
      if sb0Boundary:
        assert b"\r" not in sb0Boundary and b"\n" not in sb0Boundary and sb0Boundary.strip(), \
            "s0Boundary must be None or a string that does contins at least one non-whitespace character and does not contain '\\r' or '\\n'";
        sbContentTypeHeaderValue += b"; boundary=" + sb0Boundary;
      oSelf.oHeaders.fbReplaceHeadersForNameAndValue(b"Content-Type", sbContentTypeHeaderValue);
    if oSelf.o0AdditionalHeaders:
      oSelf.o0AdditionalHeaders.fbRemoveHeadersForName(b"Content-Type");
  
  @property
  def sb0MediaType(oSelf):
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Type");
    return o0ContentTypeHeader.sbValue.split(b";")[0].strip() if o0ContentTypeHeader else None;
  @sb0MediaType.setter
  def sb0MediaType(oSelf, sb0Value):
    oSelf.__fSetContentTypeHeader(sb0Value, oSelf.sb0Charset, oSelf.sb0Boundary);
  
  @property
  @ShowDebugOutput
  def sb0Charset(oSelf):
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Type");
    return o0ContentTypeHeader and o0ContentTypeHeader.fsb0GetNamedValue(b"charset");
  @sb0Charset.setter
  @ShowDebugOutput
  def sb0Charset(oSelf, sb0Value):
    oSelf.__fSetContentTypeHeader(oSelf.sb0MediaType, sb0Value, oSelf.sb0Boundary);
  
  @property
  @ShowDebugOutput
  def sb0Boundary(oSelf):
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Type");
    return o0ContentTypeHeader and o0ContentTypeHeader.fsb0GetNamedValue(b"boundary");
  @sb0Boundary.setter
  @ShowDebugOutput
  def sb0Boundary(oSelf, sb0Value):
    oSelf.__fSetContentTypeHeader(oSelf.sb0MediaType, oSelf.sb0Charset, sb0Value);
  
  @property
  @ShowDebugOutput
  def bChunked(oSelf):
# This is a decent sanity check, but we want to be able to work with invalid messages too.
#    if oSelf.o0AdditionalHeaders:
#      # The Transfer-Encoding is only valid in the first set of headers and not in any additional headers.
#      aoTransferEncodingHeaders = oSelf.o0AdditionalHeaders.faoGetHeadersForName(b"Transfer-Encoding");
#      if aoTransferEncodingHeaders:
#        raise cHTTPInvalidMessageException(
#          "Additional headers contain Transfer-Encoding headers",
#           o0Connection = o0Connection,
#          dxDetails = {"aoTransferEncodingHeaders": aoTransferEncodingHeaders},
#        );
    return oSelf.oHeaders.fbHasUniqueValueForName(b"Transfer-Encoding", b"Chunked");
  
  @property
  @ShowDebugOutput
  def bCloseConnection(oSelf):
    o0ConnectionHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Connection");
    if o0ConnectionHeader:
      if o0ConnectionHeader.sbLowerName == b"close":
        fShowDebugOutput("'Connection: Close' header found");
        return True;
      if o0ConnectionHeader.sbLowerName == b"keep-alive":
        fShowDebugOutput("'Connection: Keep-alive' header found");
        return False;
      # Any other values are ignored.
    # No valid Connection header found: return default, which depends on the HTTP version:
    if oSelf.sbVersion.upper() == b"HTTP/1.0":
      fShowDebugOutput("No 'Connection' header found; defaulting to 'Close' for %s" % oSelf.sbVersion);
      return True;
    elif oSelf.sbVersion.upper() == b"HTTP/1.1":
      fShowDebugOutput("No 'Connection' header found; defaulting to 'Keep-alive' for %s" % oSelf.sbVersion);
      return False;
# This is a decent sanity check, but we want to be able to work with invalid messages too.
#    raise cHTTPInvalidMessageException(
#      "Invalid HTTP version!",
#      dxDetails = {"sbVersion": oSelf.sbVersion},
#    );
    return True; # Closing the connection is the safest option.
  
  @property
  @ShowDebugOutput
  def bCompressed(oSelf):
    for sCompressionType in oSelf.asbCompressionTypes or []:
      if sCompressionType.lower() != "identity":
        return True;
    return False;
  
  @property
  @ShowDebugOutput
  def asbCompressionTypes(oSelf):
    o0ContentEncodingHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Encoding");
    return [sb.strip() for sb in o0ContentEncodingHeader.sbValue.split(b",")] if o0ContentEncodingHeader else [];
  
  @property
  def s0Data(oSelf):
    return oSelf.fs0GetData();
  def fs0GetData(oSelf, o0Connection = None):
    # Returns decompressed and decoded body based on the Content-Encoding header.
    sb0DecompressedBody = oSelf.sb0DecompressedBody;
    if sb0DecompressedBody is None:
      return None;
    sbDecompressedBody = sb0DecompressedBody; # Never None past this point.
    sb0Charset = oSelf.sb0Charset;
    if oSelf.sb0Charset is None:
      sData = "".join(chr(uByte) for uByte in sbDecompressedBody);
    else:
      try:
        sCharset = str(sb0Charset, 'ascii');
      except UnicodeError as oException:
        raise cHTTPUnhandledeCharsetException(
          "The charset provided in the Content-Type header is invalid.",
          o0Connection = o0Connection,
          dxDetails = {"sbCharset": sb0Charset},
        );
      try:
        sData = str(sbDecompressedBody, sCharset, "strict");
      except LookupError as oException:
        raise cHTTPUnhandledeCharsetException(
          "The charset provided in the Content-Type header is unknown.",
          o0Connection = o0Connection,
          dxDetails = {"sCharset": sCharset},
        );
      except UnicodeError as oException:
        raise cHTTPInvalidEncodedDataException(
          "The body does not contain valid encoded data.",
          o0Connection = o0Connection,
          dxDetails = {"sCharset": sCharset, "sbDecompressedBody": sbDecompressedBody},
        );
    return sData;
  
  @ShowDebugOutput
  def fSetData(oSelf, sData, bCloseConnectionInsteadOfUsingContentLength = False, o0Connection = None):
    # Convert Unicode string to bytes using the "charset" defined in the headers.
    # Then apply compression to the result and set it as the body of the message.
    fAssertType("sData", sData, str);
    sb0Charset = oSelf.sb0Charset;
    if sb0Charset is None:
      # Convert string to bytes, assuming string contains only byte values ('\x00'-'\xFF').
      try:
        sbUncompressedBody = bytes([ord(sChar) for sChar in sData]);
      except ValueError as oException:
        raise cHTTPInvalidEncodedDataException(
          "The data contains non-byte characters.",
          o0Connection = o0Connection,
          dxDetails = {"sData": sData},
        );
    else:
      # Convert Unicode string to bytes using charset defined in Content-Type header.
      try:
        sCharset = str(sb0Charset, "ascii");
      except UnicodeError as oException:
        raise cHTTPUnhandledeCharsetException(
          "The charset provided in the Content-Type header is invalid.",
          o0Connection = o0Connection,
          dxDetails = {"sbCharset": sb0Charset},
        );
      try:
        sbUncompressedBody = bytes(sData, sCharset, "strict");
      except LookupError as oException:
        raise cHTTPUnhandledeCharsetException(
          "The charset provided in the Content-Type header is unknown.",
          o0Connection = o0Connection,
          dxDetails = {"sCharset": sCharset},
        );
      except UnicodeError as oException:
        raise cHTTPInvalidEncodedDataException(
          "The data cannot be encoded.",
          o0Connection = o0Connection,
          dxDetails = {"sCharset": sCharset, "sData": sData},
        );
    # Sets the (optionally) compressed body of the message.
    oSelf.fApplyCompressionAndSetBody(sbUncompressedBody, bCloseConnectionInsteadOfUsingContentLength);
  
  @property
  def sb0DecompressedBody(oSelf):
    # Returns decoded and decompressed body based on the Content-Encoding header.
    sb0Data = oSelf.__sb0Body if not oSelf.bChunked else b"".join(oSelf.__a0sbBodyChunks);
    if sb0Data is None:
      return None;
    sbData = sb0Data; # Never None past this point.
    for sbCompressionType in reversed(oSelf.asbCompressionTypes):
      sbData = fsbDecompressData(sbData, sbCompressionType);
    return sbData;
  
  @ShowDebugOutput
  def fApplyCompressionAndSetBody(oSelf, sbData, bCloseConnectionInsteadOfUsingContentLength = False):
    fAssertType("sbData", sbData, bytes);
    # Sets the (optionally) compressed body of the message.
    for sbCompressionType in reversed(oSelf.asbCompressionTypes):
      sbData = fsbCompressData(sbData, sbCompressionType);
    oSelf.fSetBody(sbData, bCloseConnectionInsteadOfUsingContentLength);
  
  @property
  @ShowDebugOutput
  def sb0Body(oSelf):
    if not oSelf.bChunked:
      return oSelf.__sb0Body;
    assert oSelf.__a0sbBodyChunks is not None, \
        "bChunked == True but __a0sbBodyChunks == None !?";
    return b"".join([
      b"%X\r\n%s\r\n" % (len(sbBodyChunk), sbBodyChunk) 
      for sbBodyChunk in oSelf.__a0sbBodyChunks
    ]) + b"0\r\n\r\n";
  
  @ShowDebugOutput
  def fSetBody(oSelf, sb0Body, bCloseConnectionInsteadOfUsingContentLength = False):
    oSelf.oHeaders.fbRemoveHeadersForName(b"Transfer-Encoding");
    if oSelf.sbVersion.upper() != b"HTTP/1.1":
      bCloseConnectionInsteadOfUsingContentLength = True;
    if bCloseConnectionInsteadOfUsingContentLength:
      oSelf.oHeaders.fbReplaceHeadersForNameAndValue(b"Connection", b"Close");
      oSelf.oHeaders.fbRemoveHeadersForName(b"Content-Length");
    elif sb0Body is not None:
      # Add a 'Content-Length' header if sb0Body is not None;
      oSelf.oHeaders.fbReplaceHeadersForNameAndValue(b"Content-Length", b"%d" % len(sb0Body));
    oSelf.__sb0Body = sb0Body;
    oSelf.__a0sbBodyChunks = None;
  
  @property
  @ShowDebugOutput
  def asbBodyChunks(oSelf):
    assert oSelf.bChunked, \
        "Cannot get body chunks when chunked encoding is not enabled";
    return oSelf.__a0sbBodyChunks[:];
  
  @ShowDebugOutput
  def fSetBodyChunks(oSelf, asbBodyChunks):
    for sbBodyChunk in asbBodyChunks:
      assert sbBodyChunk, \
          "Cannot add empty body chunks";
    oSelf.oHeaders.fbRemoveHeadersForName(b"Content-Length");
    oSelf.oHeaders.fbReplaceHeadersForNameAndValue(b"Transfer-Encoding", b"Chunked");
    oSelf.__sb0Body = None;
    oSelf.__a0sbBodyChunks = asbBodyChunks[:];
  
  @ShowDebugOutput
  def fAddBodyChunk(oSelf, sbBodyChunk):
    fAssertType("sbBodyChunk", sbBodyChunk, bytes);
    assert len(sbBody) > 0, \
        "Cannot add an empty chunk!"
    if not oSelf.bChunked:
      assert oSelf.__sb0Body is None, \
          "Cannot add a chunk if body is set";
      oSelf.fSetBodyChunks([sbBodyChunk]);
    else:
      oSelf.__a0sbBodyChunks.append(sbBodyChunk);
  
  @ShowDebugOutput
  def fRemoveBody(oSelf):
    oSelf.oHeaders.fbRemoveHeadersForName(b"Content-Encoding");
    oSelf.oHeaders.fbRemoveHeadersForName(b"Content-Length");
    oSelf.oHeaders.fbRemoveHeadersForName(b"Transfer-Encoding", b"Chunked");
    oSelf.__sb0Body = None;
    oSelf.__a0sbBodyChunks = None;
  
  # application/x-www-form-urlencoded
  @property
  @ShowDebugOutput
  def d0Form_sValue_by_sName(oSelf):
    # convert the decoded and decompressed body to form name-value pairs.
    sb0MediaType = oSelf.sb0MediaType;
    if sb0MediaType is None or sb0MediaType.lower() != b"application/x-www-form-urlencoded":
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
    assert d0Form_sValue_by_sName is not None, \
        "HTTP Message does not contain URL encoded form data.";
    dForm_sValue_by_sName = d0Form_sValue_by_sName;
    for sOtherName in dForm_sValue_by_sName.keys():
      if sLowerStrippedName == sOtherName.lower():
        del dForm_sValue_by_sName[sOtherName];
    if s0Value is not None:
      dForm_sValue_by_sName[sName] = s0Value;
    oSelf.fApplyCompressionAndSetBody(fsbURLEncodedNameValuePairsToBytesString(dForm_sValue_by_sName));
  
  @ShowDebugOutput
  def fRemoveFormValue(oSelf, sName):
    oSelf.fSetFormValue(sName, None);
  
  # Authorization
  @ShowDebugOutput
  def ftsb0GetBasicAuthorization(oSelf):
    sb0Authorization = oSelf.oHeaders.fs0GetUniqueHeaderValue(b"Authorization");
    if sb0Authorization is None:
      return (None, None);
    sBbasic, sbBase64EncodedUserNameColonPassword = sb0Authorization.strip().split(b" ", 1);
    if sbBasic.lower() != b"basic ":
      return (None, None);
    try:
      sbUserNameColonPassword = base64.b64decode(sbBase64EncodedUserNameColonPassword.lstrip());
    except Exception as oException:
      return (None, None);
    if b":" in sbUserNameColonPassword:
      sbUserName, sbPassword = sbUserNameColonPassword.split(":", 1);
    else:
      sbUserName = sbUserNameColonPassword;
      sbPassword = None;
    return (sbUserName, sbPassword);
  
  @ShowDebugOutput
  def fSetBasicAuthorization(oSelf, sbUserName, sbPassword):
    sbBase64EncodedUserNameColonPassword = base64.b64encode("%s:%s" % (sbUserName, sbPassword));
    oSelf.oHeaders.fbReplaceHeadersForNameAndValue(b"Authorization", b"basic %s" % sbBase64EncodedUserNameColonPassword);
  
  def fsbSerialize(oSelf):
    return b"\r\n".join([
      oSelf.fsbGetStatusLine(),
    ] + oSelf.oHeaders.fasbGetHeaderLines() + [
      b"",
      oSelf.sb0Body or b"",
    ]);
  
  def fasGetDetails(oSelf):
    # Make sure not to call *any* method that has ShowDebugOutput, as this causes
    # fasGetDetails to get called again, resulting in infinite recursion.
    if oSelf.oHeaders.fbHasUniqueValueForName(b"Transfer-Encoding", b"Chunked"):
      asbChunks = oSelf.__a0sbBodyChunks;
      sBodyDetails = "%d bytes body in %d chunks" % (sum([len(sbChunk) for sbChunk in asbChunks]), len(asbChunks));
    else:
      sb0Body = oSelf.__sb0Body;
      sBodyDetails = "%d bytes body" % len(sb0Body) if sb0Body is not None else "no body";
    
    o0ContentEncodingHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Encoding", oSelf.o0AdditionalHeaders);
    sCompressionTypes = ">".join([str(s.strip(), 'latin1') for s in o0ContentEncodingHeader.sbValue.split(b",")]) if o0ContentEncodingHeader else None;
    
    bCloseConnection = oSelf.oHeaders.fbHasUniqueValueForName(b"Connection", b"Close");
    
    o0HostHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Host", oSelf.o0AdditionalHeaders);
    o0ContentTypeHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Content-Type", oSelf.o0AdditionalHeaders);
    s0MediaType = str(o0ContentTypeHeader.sbValue.split(b";")[0].strip(), 'latin1') if o0ContentTypeHeader else None;
    return [s for s in [
      str(oSelf.fsbGetStatusLine(), 'latin1'),
      "%d headers" % oSelf.oHeaders.uNumberOfHeaders if not gbShowAllHeadersInStrReturnValue else None,
      "Host: %s" % str(o0HostHeader.sbValue, 'latin1') if o0HostHeader and not gbShowAllHeadersInStrReturnValue else None,
    ] if s] + (
      [
       str(b"%s: %s" % (oHeader.sbName, oHeader.sbValue), 'latin1')
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

for cException in acExceptions:
  setattr(iHTTPMessage, cException.__name__, cException);
