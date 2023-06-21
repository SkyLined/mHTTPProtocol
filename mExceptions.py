class cHTTPException(Exception):
  def __init__(oSelf, sMessage, *, o0Connection = None, dxDetails = None):
    assert isinstance(dxDetails, dict), \
        "dxDetails must be a dict, not %s" % repr(dxDetails);
    oSelf.sMessage = sMessage;
    oSelf.o0Connection = o0Connection;
    oSelf.dxDetails = dxDetails;
    Exception.__init__(oSelf, sMessage, o0Connection, dxDetails);
  
  def fasDetails(oSelf):
    return (
      (["Remote: %s" % str(oSelf.o0Connection.sbRemoteAddress, "ascii", "strict")] if oSelf.o0Connection else [])
      + ["%s: %s" % (str(sName), repr(xValue)) for (sName, xValue) in oSelf.dxDetails.items()]
    );
  def __str__(oSelf):
    return "%s (%s)" % (oSelf.sMessage, ", ".join(oSelf.fasDetails()));
  def __repr__(oSelf):
    return "<%s.%s %s>" % (oSelf.__class__.__module__, oSelf.__class__.__name__, oSelf);

class cHTTPInvalidMessageException(cHTTPException):
  # Indicates that data does not contain a valid HTTP Message.
  pass;

class cHTTPInvalidEncodedDataException(cHTTPInvalidMessageException):
  # Indicates that data compression or decompression using the compression
  # technique specified in the "Content-Encoding" header of the http message
  # failed, or that encoding from or decoding to Unicode using the character
  # encoding technique specified in the "Content-Type" header failed.
  # If no "charset" is provided, the data cannot be encoded because it contains
  # Unicode characters that are not bytes (i.e. not in range '\x00'-'\xFF')
  pass;

class cHTTPUnhandledCharsetException(cHTTPInvalidMessageException):
  # The "charset" provided in the "Content-Type" header of a HTTP message is
  # not known, so the data cannot be decoded from or encoded to the message
  # body.
  pass;

class cHTTPInvalidURLException(cHTTPException):
  # Indicates that data does not contain a valid HTTP URL.
  pass;

class cHTTPMaxConnectionsToServerReachedException(cHTTPException):
  # Indicates the client would need to create more connections to the server than allowed.
  pass;

acExceptions = [
  cHTTPException,
  cHTTPInvalidMessageException,
  cHTTPInvalidEncodedDataException,
  cHTTPUnhandledCharsetException,
  cHTTPInvalidURLException,
  cHTTPMaxConnectionsToServerReachedException,
];