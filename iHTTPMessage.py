import base64;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

from mNotProvided import \
    fAssertType, \
    fbIsProvided, \
    fxGetFirstProvidedValue, \
    zNotProvided;

from .cHTTPHeaders import cHTTPHeaders;
from .fdsURLDecodedNameValuePairsFromString import fdsURLDecodedNameValuePairsFromString;
from .fsbCompressData import fsbCompressData;
from .fsbDecompressData import fsbDecompressData;
from .fsbURLEncodedNameValuePairsToBytesString import fsbURLEncodedNameValuePairsToBytesString;
from .mExceptions import \
    acExceptions, \
    cHTTPInvalidEncodedDataException, \
    cHTTPInvalidMessageException, \
    cHTTPUnhandledCharsetException;

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
  def foFromBytesString(cClass, sbData, o0Connection = None, bStrictErrorChecking = True):
    asbStatusHeadersAndBody = sbData.split(b"\r\n\r\n", 1);
    # If the data ends after the last header line (i.e. it ends with "\r\n")
    # the below will result in `[b"...\r\n"]`. Otherwise it ends with the last
    # headerline without a CRLF. We will have to remove the CRLF in the first case
    # before splitting the rest at CRLFs, to avoid having an empty string at the end:
    asbStatusHeadersLines = asbStatusHeadersAndBody[0].rstrip(b"\r\n").split(b"\r\n");
    sbStatusLine = asbStatusHeadersLines.pop(0);
    asbHeadersLines = asbStatusHeadersLines;
    sb0Body = None if len(asbStatusHeadersAndBody) == 1 else asbStatusHeadersAndBody[1];
    dxStatusLineArguments = cClass.fdxParseStatusLine(
      sbStatusLine,
      o0Connection = o0Connection,
      bStrictErrorChecking = bStrictErrorChecking,
    );
    oHeaders = cClass.foParseHeaderLines(
      asbHeadersLines,
      o0Connection = o0Connection,
      bStrictErrorChecking = bStrictErrorChecking,
    );
    return cClass(
      o0zHeaders = oHeaders,
      sb0Body = sb0Body,
      **dxStatusLineArguments,
    );
      
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
    *,
    sbzVersion = zNotProvided,
    o0zHeaders = zNotProvided,
    sb0Body = None,
    s0Data = None,
    a0sbBodyChunks = None,
    o0AdditionalHeaders = None,
    bAddContentLengthHeader = True,
    bCloseConnection = False,
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
    
    bChunked = oSelf.oHeaders.fbHasUniqueValueForName(b"Transfer-Encoding", b"Chunked");
    if sb0Body is not None:
      assert not bChunked, \
            "Cannot provide sb0Body (%s) with a \"Transfer-Encoded: Chunked\" header!" % repr(sb0Body);
      oSelf.fSetBody(
        sb0Body,
        bAddContentLengthHeader = bAddContentLengthHeader,
        bCloseConnection = bCloseConnection,
      );
    else:
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
    # The sender can tell us the body is compressed using one algorithm but
    # encode it using another. The code can deal with this if you set the 
    # `bTryOtherCompressionTypesOnFailure` argument to True when attempting to
    # decompress the body: it will attempt every single decompression algorithm
    # it knows until it finds one that works. If you do this and the actual
    # decompression algorithm(s) used differ from those provided in the header
    # this property will be set to a list of the decompression algorithms used.
    oSelf.__a0sbActualCompressionTypes = None;
  
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
  def bIndicatesConnectionShouldBeClosed(oSelf):
    o0ConnectionHeader = oSelf.oHeaders.fo0GetUniqueHeaderForName(b"Connection");
    if o0ConnectionHeader:
      for sbTokenWithOptionalWhitespace in o0ConnectionHeader.sbValue.split(b","):
        sbLowercaseToken = sbTokenWithOptionalWhitespace.strip().lower();
        if sbLowercaseToken == b"close":
          return True;
    if oSelf.sbVersion == b"HTTP/1.1":
      return False;
    return True;

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
  def fs0GetData(oSelf,
    o0Connection = None,
    bTryOtherCompressionTypesOnFailure = False,
    bIgnoreDecompressionFailures = False,
  ):
    # Returns decompressed and decoded body based on the Content-Encoding header.
    sb0DecompressedBody = oSelf.fsb0GetDecompressedBody(
      bTryOtherCompressionTypesOnFailure = bTryOtherCompressionTypesOnFailure,
      bIgnoreDecompressionFailures = bIgnoreDecompressionFailures,
    );
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
        raise cHTTPUnhandledCharsetException(
          "The charset provided in the Content-Type header is invalid.",
          o0Connection = o0Connection,
          dxDetails = {"sbCharset": sb0Charset},
        );
      try:
        sData = str(sbDecompressedBody, sCharset, "strict");
      except LookupError as oException:
        raise cHTTPUnhandledCharsetException(
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
  def fSetData(oSelf,
    sData,
    *,
    bAddContentLengthHeader = True,
    bCloseConnection = False,
    o0Connection = None,
  ):
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
        raise cHTTPUnhandledCharsetException(
          "The charset provided in the Content-Type header is invalid.",
          o0Connection = o0Connection,
          dxDetails = {"sbCharset": sb0Charset},
        );
      try:
        sbUncompressedBody = bytes(sData, sCharset, "strict");
      except LookupError as oException:
        raise cHTTPUnhandledCharsetException(
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
    oSelf.fApplyCompressionAndSetBody(
      sbUncompressedBody,
      bAddContentLengthHeader = bAddContentLengthHeader,
      bCloseConnection = bCloseConnection,
    );
  
  @property
  def sb0DecompressedBody(oSelf):
    return oSelf.fsb0GetDecompressedBody();
  
  @property
  def asbActualCompressionTypes(oSelf):
    # We'll decompress the body, trying to fix errors and ignoring them if we cannot
    # to get the actual compression types as best we can.
    oSelf.fsb0GetDecompressedBody(
      bTryOtherCompressionTypesOnFailure = True,
      bIgnoreDecompressionFailures = True,
    );
    return oSelf.__a0sbActualCompressionTypes;
  
  def fsb0GetDecompressedBody(oSelf,
    bTryOtherCompressionTypesOnFailure = False,
    bIgnoreDecompressionFailures = False,
  ):
    oSelf.__a0sbActualCompressionTypes = [];
    # Returns decoded and decompressed body based on the Content-Encoding header.
    sb0Data = oSelf.__sb0Body if not oSelf.bChunked else b"".join(oSelf.__a0sbBodyChunks);
    if sb0Data is None:
      return None;
    sbData = sb0Data; # Never None past this point.
    # We'll keep track of the actual list of compression types processed. This
    # tells you at what point decompression fails if there are multiple compressions
    # applied and decompression fails
    # if `bTryOtherCompressionTypesOnFailure` is True, this tells you the actual
    # compression types found, in case there is a mismatch with the Content-Encoding header.
    for sbCompressionType in reversed(oSelf.asbCompressionTypes):
      try:
        sbData = fsbDecompressData(sbData, sbCompressionType);
      except cHTTPInvalidEncodedDataException as oOriginalException:
        # Some servers will tell us the wrong encoding type. If asked, this code
        # can try all known compression types to see if the message can be decoded
        # regardless.
        if not bTryOtherCompressionTypesOnFailure:
          # we'll throw an error unless we're asked to completely ignore de-encoding errors.
          if bIgnoreDecompressionFailures:
            continue;
          raise;
        for sbCompressionType in fsbDecompressData.asbSupportedCompressionTypes:
          try:
            sbData = fsbDecompressData(sbData, sbCompressionType);
          except cHTTPInvalidEncodedDataException:
            pass;
          else:
            # The list of compression types in the message is invalid but we found a way
            # to work around that.
            break;
        else:
          # Unable to decompress with any known algorithm: throw an exception if this
          # should not be ignored.
          if bIgnoreDecompressionFailures:
            continue; # do not add anything to the actual compression types list
          raise oOriginalException;
      oSelf.__a0sbActualCompressionTypes.append(sbCompressionType);
    return sbData;

  @ShowDebugOutput
  def fApplyCompressionAndSetBody(oSelf,
    sbData,
    *,
    bAddContentLengthHeader = True,
    bCloseConnection = False,
  ):
    fAssertType("sbData", sbData, bytes);
    # Sets the (optionally) compressed body of the message.
    for sbCompressionType in reversed(oSelf.asbCompressionTypes):
      sbData = fsbCompressData(sbData, sbCompressionType);
    oSelf.fSetBody(
      sbData,
      bAddContentLengthHeader = bAddContentLengthHeader,
      bCloseConnection = bCloseConnection,
    );
  
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
  def fSetBody(oSelf,
    sb0Body,
    *,
    bAddContentLengthHeader = True,
    bCloseConnection = False,
  ):
    oSelf.oHeaders.fbRemoveHeadersForName(b"Transfer-Encoding");
    oSelf.__sb0Body = sb0Body;
    oSelf.__a0sbBodyChunks = None;
    if bAddContentLengthHeader:
      oSelf.oHeaders.fbReplaceHeadersForNameAndValue(b"Content-Length", b"%d" % len(oSelf.__sb0Body));
    if bCloseConnection:
      oSelf.oHeaders.fbReplaceHeadersForNameAndValue(b"Connection", b"Close");
  
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
    assert len(sbBodyChunk) > 0, \
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
    sLowerStrippedName = sName.lower();
    d0Form_sValue_by_sName = oSelf.d0Form_sValue_by_sName;
    if d0Form_sValue_by_sName is None:
      oSelf.sb0MediaType = b"application/x-www-form-urlencoded";
      dForm_sValue_by_sName = {};
    else:
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
    sbBasic, sbBase64EncodedUserNameColonPassword = sb0Authorization.strip().split(b" ", 1);
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
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));

for cException in acExceptions:
  setattr(iHTTPMessage, cException.__name__, cException);
