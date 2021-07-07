class cHTTPException(Exception):
  def __init__(oSelf, sMessage, dxDetails):
    oSelf.sMessage = sMessage;
    oSelf.dxDetails = dxDetails;
    Exception.__init__(oSelf, sMessage, dxDetails);
  
  def __repr__(oSelf):
    return "<%s %s>" % (oSelf.__class__.__name__, oSelf);
  def __str__(oSelf):
    sDetails = ", ".join("%s: %s" % (str(sName), repr(xValue)) for (sName, xValue) in oSelf.dxDetails.items());
    return "%s (%s)" % (oSelf.sMessage, sDetails);

class cHTTPInvalidMessageException(cHTTPException):
  # Indicates that data does not contain a valid HTTP Message.
  pass;

class cHTTPInvalidEncodedDataException(cHTTPInvalidMessageException):
  # Indicates that data cannot be encoded from or decoded to Unicode using the
  # "charset" provided in the "Content-Type" header of a HTTP message.
  # If no "charset" is provided, the data cannot be encoded because it contains
  # Unicode characters that are not bytes (i.e. not in range '\x00'-'\xFF')
  pass;

class cHTTPUnhandledCharsetException(cHTTPInvalidMessageException):
  # The "charset" provided in the "Content-Type" header of a HTTP message is
  # not known, so the data cannot be decoded from or encoded to the message
  # body.
  pass;

class cInvalidURLException(cHTTPException):
  # Indicates that data does not contain a valid HTTP URL.
  pass;

