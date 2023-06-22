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

from .dsbHTTPCommonReasonPhrase_by_uStatusCode import dsbHTTPCommonReasonPhrase_by_uStatusCode;
from .iHTTPMessage import iHTTPMessage;
from .mExceptions import *;

class cHTTPResponse(iHTTPMessage):
  uDefaultStatusCode = 200;
  ddDefaultHeader_sbValue_by_sbName_by_sbHTTPVersion = {
    b"HTTP/1.0": {
      b"Connection": b"Close",
      b"Cache-Control": b"No-Cache, Must-Revalidate",
      b"Expires": b"Wed, 16 May 2012 04:01:53 GMT", # 1337
      b"Pragma": b"No-Cache",
    },
    b"HTTP/1.1": {
      b"Connection": b"Keep-Alive",
      b"Cache-Control": b"No-Cache, Must-Revalidate",
      b"Expires": b"Wed, 16 May 2012 04:01:53 GMT", # 1337
    },
  };
  
  @staticmethod
  @ShowDebugOutput
  def fdxParseStatusLine(sbStatusLine, o0Connection = None, bStrictErrorChecking = True):
    asbComponents = sbStatusLine.split(b" ", 2);
    if not bStrictErrorChecking and len(asbComponents) == 2:
      asbComponents += [""]; # Accept missing reason phrase.
    elif len(asbComponents) != 3:
      raise cHTTPInvalidMessageException(
        "The remote send an invalid status line.",
        o0Connection = o0Connection,
        dxDetails = {"sbStatusLine": sbStatusLine},
      );
    (sbVersion, sbStatusCode, sbReasonPhrase) = asbComponents;
    try:
      if bStrictErrorChecking and len(sbStatusCode) != 3:
        raise ValueError();
      uStatusCode = int(sbStatusCode);
    except ValueError:
      uStatusCode = 0;
    if bStrictErrorChecking:
      dxDetails = {
        "sbStatusLine": sbStatusLine,
        "sbVersion": sbVersion,
        "uzStatusCode": uStatusCode,
        "sbReasonPhrase": sbReasonPhrase
      };  
      if sbVersion not in [b"HTTP/1.0", b"HTTP/1.1"]:
        raise cHTTPInvalidMessageException(
          "The remote send an invalid HTTP version in the status line.",
          o0Connection = o0Connection,
          dxDetails = dxDetails,
        );
      if uStatusCode < 100 or uStatusCode > 599:
        raise cHTTPInvalidMessageException(
          "The remote send an invalid status code in the status line.",
          o0Connection = o0Connection,
          dxDetails = dxDetails,
        );
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    # Return a dictionary that can be used as arguments to __init__
    return {"sbzVersion": sbVersion, "uzStatusCode": uStatusCode, "sbzReasonPhrase": sbReasonPhrase};
  
  @staticmethod
  def fsbGetDefaultReasonPhraseForStatus(uStatusCode):
    return dsbHTTPCommonReasonPhrase_by_uStatusCode.get(uStatusCode, b"Unspecified");  
  
  @ShowDebugOutput
  def __init__(oSelf,
    *,
    sbzVersion = zNotProvided,
    uzStatusCode = zNotProvided,
    sbzReasonPhrase = zNotProvided,
    o0zHeaders = zNotProvided,
    sb0Body = None,
    s0Data = None,
    a0sbBodyChunks = None,
    o0AdditionalHeaders = None,
  ):
    oSelf.uStatusCode = fxGetFirstProvidedValue(uzStatusCode, oSelf.uDefaultStatusCode);
    oSelf.sbReasonPhrase = (
      sbzReasonPhrase if fbIsProvided(sbzReasonPhrase) else
      oSelf.fsbGetDefaultReasonPhraseForStatus(oSelf.uStatusCode)
    );
    iHTTPMessage.__init__(oSelf,
      sbzVersion = sbzVersion,
      o0zHeaders = o0zHeaders,
      sb0Body = sb0Body,
      s0Data = s0Data,
      a0sbBodyChunks = a0sbBodyChunks,
      o0AdditionalHeaders = o0AdditionalHeaders,
    );
  
  @property
  def uStatusCode(oSelf):
    return oSelf.__uStatusCode;
  @uStatusCode.setter
  def uStatusCode(oSelf, uStatusCode):
    assert (isinstance(uStatusCode, int) and uStatusCode in range(100, 600)), \
        "Status code must be an unsigned integer in the range 100-999, not %s" % repr(uStatusCode);
    oSelf.__uStatusCode = uStatusCode;
  
  @property
  def sbReasonPhrase(oSelf):
    return oSelf.__sbReasonPhrase;
  @sbReasonPhrase.setter
  def sbReasonPhrase(oSelf, sbReasonPhrase): # setting to b"" will result in it being set to a common message for the current status code.
    fAssertType("sbReasonPhrase", sbReasonPhrase, bytes);
    oSelf.__sbReasonPhrase = sbReasonPhrase or oSelf.fsbGetDefaultReasonPhraseForStatus(oSelf.__uStatusCode);
  
  def fsbGetStatusLine(oSelf):
    return b"%s %03d %s" % (oSelf.sbVersion, oSelf.__uStatusCode, oSelf.__sbReasonPhrase);
  