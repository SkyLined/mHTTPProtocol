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

from .dsHTTPCommonReasonPhrase_by_uStatusCode import dsHTTPCommonReasonPhrase_by_uStatusCode;
from .iHTTPMessage import iHTTPMessage;
from .mExceptions import *;

class cHTTPResponse(iHTTPMessage):
  uDefaultStatusCode = 200;
  ddDefaultHeader_sValue_by_sName_by_sHTTPVersion = {
    "HTTP/1.0": {
      "Connection": "Close",
      "Cache-Control": "No-Cache, Must-Revalidate",
      "Expires": "Wed, 16 May 2012 04:01:53 GMT", # 1337
      "Pragma": "No-Cache",
    },
    "HTTP/1.1": {
      "Connection": "Keep-Alive",
      "Cache-Control": "No-Cache, Must-Revalidate",
      "Expires": "Wed, 16 May 2012 04:01:53 GMT", # 1337
    },
  };
  
  @staticmethod
  @ShowDebugOutput
  def fdxParseStatusLine(sStatusLine):
    asComponents = sStatusLine.split(" ", 2);
    if len(asComponents) != 3:
      raise cHTTPInvalidMessageException("The remote send an invalid status line.", sStatusLine);
    sVersion, sStatusCode, sReasonPhrase = asComponents;
    if sVersion not in ["HTTP/1.0", "HTTP/1.1"]:
      raise cHTTPInvalidMessageException("The remote send an invalid HTTP version in the status line.", sVersion);
    try:
      if len(sStatusCode) != 3:
        raise ValueError();
      uStatusCode = long(sStatusCode);
      if uStatusCode < 100 or uStatusCode > 599:
        raise ValueError();
    except ValueError:
      raise cHTTPInvalidMessageException("The remote send an invalid status code in the status line.", sStatusCode);
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    # Return a dictionary that can be used as arguments to __init__
    return {"szVersion": sVersion, "uzStatusCode": uStatusCode, "szReasonPhrase": sReasonPhrase};
  
  @staticmethod
  def fsGetDefaultReasonPhraseForStatus(uStatusCode):
    return dsHTTPCommonReasonPhrase_by_uStatusCode.get(uStatusCode, "Unspecified");  
  
  @ShowDebugOutput
  def __init__(oSelf,
    szVersion = zNotProvided,
    uzStatusCode = zNotProvided,
    szReasonPhrase = zNotProvided,
    o0zHeaders = zNotProvided,
    s0Body = None,
    s0Data = None,
    a0sBodyChunks = None,
    o0AdditionalHeaders = None,
    bAutomaticallyAddContentLengthHeader = False
  ):
    oSelf.uStatusCode = fxGetFirstProvidedValue(uzStatusCode, oSelf.uDefaultStatusCode);
    oSelf.sReasonPhrase = (
      szReasonPhrase if fbIsProvided(szReasonPhrase) else
      oSelf.fsGetDefaultReasonPhraseForStatus(oSelf.uStatusCode)
    );
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
  def uStatusCode(oSelf):
    return oSelf.__uStatusCode;
  @uStatusCode.setter
  def uStatusCode(oSelf, uStatusCode):
    assert (isinstance(uStatusCode, (long, int)) and uStatusCode in xrange(100, 600)), \
        "Status code must be an unsigned integer in the range 100-999, not %s" % repr(uStatusCode);
    oSelf.__uStatusCode = uStatusCode;
  
  @property
  def sReasonPhrase(oSelf):
    return oSelf.__sReasonPhrase;
  @sReasonPhrase.setter
  def sReasonPhrase(oSelf, sReasonPhrase): # setting to "" will result in it being set to a common message for the current status code.
    assert isinstance(sReasonPhrase, str), \
        "The reason phrase must be a str, not %s" % repr(sReasonPhrase);
    oSelf.__sReasonPhrase = sReasonPhrase or oSelf.fsGetDefaultReasonPhraseForStatus(oSelf.__uStatusCode);
  
  def fsGetStatusLine(oSelf):
    return "%s %03d %s" % (oSelf.sVersion, oSelf.__uStatusCode, oSelf.__sReasonPhrase);
  