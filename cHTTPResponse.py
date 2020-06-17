try: # mDebugOutput use is Optional
  from mDebugOutput import *;
except: # Do nothing if not available.
  ShowDebugOutput = lambda fxFunction: fxFunction;
  fShowDebugOutput = lambda sMessage: None;
  fEnableDebugOutputForModule = lambda mModule: None;
  fEnableDebugOutputForClass = lambda cClass: None;
  fEnableAllDebugOutput = lambda: None;
  cCallStack = fTerminateWithException = fTerminateWithConsoleOutput = None;

from .dsHTTPCommonReasonPhrase_by_uStatusCode import dsHTTPCommonReasonPhrase_by_uStatusCode;
from .iHTTPMessage import iHTTPMessage;

class cHTTPResponse(iHTTPMessage):
  @staticmethod
  @ShowDebugOutput
  def fdxParseStatusLine(sStatusLine):
    asComponents = sStatusLine.split(" ", 2);
    if len(asComponents) != 3:
      raise iHTTPMessage.cInvalidMessageException("The remote send an invalid status line.", sStatusLine);
    sVersion, sStatusCode, sReasonPhrase = asComponents;
    if sVersion not in ["HTTP/1.0", "HTTP/1.1"]:
      raise iHTTPMessage.cInvalidMessageException("The remote send an invalid HTTP version in the status line.", sVersion);
    try:
      if len(sStatusCode) != 3:
        raise ValueError();
      uStatusCode = long(sStatusCode);
      if uStatusCode < 100 or uStatusCode > 599:
        raise ValueError();
    except ValueError:
      raise iHTTPMessage.cInvalidMessageException("The remote send an invalid status code in the status line.", sStatusCode);
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    return {"szVersion": sVersion, "uzStatusCode": uStatusCode, "szReasonPhrase": sReasonPhrase};
  
  @ShowDebugOutput
  def __init__(oSelf, szVersion = None, uzStatusCode = None, szReasonPhrase = None, ozHeaders = None, szBody = None, szData = None, azsBodyChunks = None, ozAdditionalHeaders = None):
    assert uzStatusCode is None or (isinstance(uzStatusCode, (long, int)) and uzStatusCode in xrange(100, 600)), \
        "Status code must be an unsigned integer in the range 100-999, not %s" % repr(uzStatusCode);
    oSelf.uStatusCode = uzStatusCode;
    oSelf.sReasonPhrase = szReasonPhrase;
    iHTTPMessage.__init__(oSelf, szVersion, ozHeaders, szBody, szData, azsBodyChunks, ozAdditionalHeaders);
  
  @property
  def uStatusCode(oSelf):
    return oSelf.__uStatusCode;
  @uStatusCode.setter
  def uStatusCode(oSelf, uzStatusCode): # setting to None or 0 will result in it being set to 200
    oSelf.__uStatusCode = uzStatusCode or 200;
  
  @property
  def sReasonPhrase(oSelf):
    return oSelf.__sReasonPhrase;
  @sReasonPhrase.setter
  def sReasonPhrase(oSelf, szReasonPhrase): # setting to None or "" will result in it being set to a common message for the current status code.
    oSelf.__sReasonPhrase = szReasonPhrase or dsHTTPCommonReasonPhrase_by_uStatusCode.get(oSelf.__uStatusCode, "Unspecified");
  
  def fsGetStatusLine(oSelf):
    return "%s %03d %s" % (oSelf.sVersion, oSelf.__uStatusCode, oSelf.__sReasonPhrase);
  