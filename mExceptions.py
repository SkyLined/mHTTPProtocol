class cProtocolException(Exception):
  def __init__(oSelf,
    sMessage: str,
    *,
    sbData: bytes,
  ):
    oSelf.sMessage = sMessage;
    oSelf.sbData = sbData;
    Exception.__init__(oSelf, sMessage, sbData);
  
  def fasDetails(oSelf) -> list[str]:
    return ["sbData: %s" % repr(oSelf.sbData)[1:]];
  def __str__(oSelf) -> str:
    return "%s (%s)" % (oSelf.sMessage, ", ".join(oSelf.fasDetails()));
  def __repr__(oSelf) -> str:
    return "<%s.%s %s>" % (oSelf.__class__.__module__, oSelf.__class__.__name__, oSelf);

## HTTP MESSAGE ################################################################
class cInvalidMessageException(cProtocolException):
  # Indicates that data does not contain a valid HTTP Message.
  pass;

## CHARACTER ENCODING ##########################################################
class cCharsetValueException(cProtocolException):
  pass;

class cInvalidCharsetValueException(cCharsetValueException):
  pass;

class cUnhandledCharsetValueException(cCharsetValueException):
  pass;

# En-/decoding errors have the same base class, but different subclasses.
class cDataCodingWithCharsetException(cProtocolException):
  def __init__(oSelf,
    sMessage: str,
    *,
    sbData: bytes,
    sb0Charset: bytes | None,
  ):
    oSelf.sb0Charset = sb0Charset;
    cProtocolException.__init__(oSelf, sMessage, sbData = sbData);

  def fasDetails(oSelf) -> list[str]:
    return cProtocolException.fasDetails(oSelf) + [
      "sb0Charset: %s" % repr(oSelf.sb0Charset)[1:] if oSelf.sb0Charset is not None else "None",
    ];

class cDataCannotBeDecodedWithCharsetException(cDataCodingWithCharsetException):
  pass;

class cDataCannotBeEncodedWithCharsetException(cDataCodingWithCharsetException):
  pass;

## CHUNKED ENCODING ############################################################
class cInvalidChunkedDataException(cProtocolException):
  pass;

class cInvalidChunkHeaderException(cInvalidChunkedDataException):
  pass;

class cInvalidChunkSizeException(cInvalidChunkHeaderException):
  pass;

class cInvalidChunkBodyException(cInvalidChunkedDataException):
  pass;

class cInvalidTrailerException(cInvalidChunkedDataException):
  pass;

## COMPRESSION #################################################################
# (De-)Compression errors have the same base class, but different subclasses.
class cCompressionWithTypeException(cProtocolException):
  def __init__(oSelf,
    sMessage: str,
    *,
    sbData: bytes,
    sbCompressionType: bytes | None,
  ):
    oSelf.sbCompressionType = sbCompressionType;
    cProtocolException.__init__(oSelf, sMessage, sbData = sbData);

  def fasDetails(oSelf) -> list[str]:
    return cProtocolException.fasDetails(oSelf) + [
      "sbCompressionType: %s" % repr(oSelf.sbCompressionType)[1:] if oSelf.sbCompressionType is not None else "None",
    ];


class cInvalidCompressedDataException(cCompressionWithTypeException):
  pass;

class cUnhandledCompressionTypeValueException(cCompressionWithTypeException):
  pass;

## HEADERS #####################################################################
class cInvalidHeaderException(cProtocolException):
  pass;

### URL #######################################################################
class cInvalidURLException(cProtocolException):
  pass;