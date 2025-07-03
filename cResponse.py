try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

from mNotProvided import (
  fAssertType,
  fAssertTypes,
  fbIsProvided,
  fxGetFirstProvidedValue,
  zNotProvided
);

from .dsbHTTPCommonReasonPhrase_by_uStatusCode import dsbHTTPCommonReasonPhrase_by_uStatusCode;
from .iMessage import iMessage;
from .mExceptions import *;

class cResponse(iMessage):
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
  bCanHaveBodyIfConnectionCloseHeaderIsPresent = True;
  
  @staticmethod
  @ShowDebugOutput
  def fdxDeserializeStartLine(
    sbStartLine: bytes,
  ) -> dict:
    asbComponents = sbStartLine.split(b" ", 2);
    if len(asbComponents) == 2:
      asbComponents += [""]; # Accept missing reason phrase.
    elif len(asbComponents) != 3:
      raise cInvalidMessageException(
        "The response start line is invalid.",
        sbData = sbStartLine,
      );
    (sbVersion, sbStatusCode, sbReasonPhrase) = asbComponents;
    if not sbVersion.startswith(b"HTTP/"):
      raise cInvalidMessageException(
        "The HTTP version in the response start line is invalid.",
        sbData = sbStartLine,
      );
    try:
      uStatusCode = int(sbStatusCode);
    except ValueError:
      raise cInvalidMessageException(
        "The HTTP status code in the response start line is invalid.",
        sbData = sbStartLine,
      );
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    # Return a dictionary that can be used as arguments to __init__
    return {
      "sbzVersion": sbVersion,
      "uzStatusCode": uStatusCode,
      "sbzReasonPhrase": sbReasonPhrase,
    };
  
  @staticmethod
  def fsb0GetDefaultReasonPhraseForStatus(
    uStatusCode: int,
  ) -> bytes:
    return dsbHTTPCommonReasonPhrase_by_uStatusCode.get(uStatusCode, b"Unspecified");  
  
  @ShowDebugOutput
  def __init__(oSelf,
    *,
    uzStatusCode: int | None | type(zNotProvided) = zNotProvided,
    sbzReasonPhrase: bytes | None | type(zNotProvided) = zNotProvided,
    **dxMessageConstructorArguments,
  ):
    fAssertTypes({
      "uzStatusCode": (uzStatusCode, int, zNotProvided),
      "sbzReasonPhrase": (sbzReasonPhrase, bytes, zNotProvided),
    });
    oSelf.uStatusCode = fxGetFirstProvidedValue(uzStatusCode, oSelf.uDefaultStatusCode);
    oSelf.sbReasonPhrase = (
      sbzReasonPhrase if fbIsProvided(sbzReasonPhrase) else
      oSelf.fsb0GetDefaultReasonPhraseForStatus(oSelf.uStatusCode) or
      b"Unspecified" # Default value if no reason phrase is provided and no
                     # default value is known for the status code.
    );
    iMessage.__init__(oSelf, **dxMessageConstructorArguments);

  def fdxGetCloneConstructorArguments(oSelf, **dxOverwrittenConstructorArguments) -> dict:
    dxConstructorArguments = dict(dxOverwrittenConstructorArguments);
    # Add any required constructor arguments for a clone that have not been overwritten:
    if "uzStatusCode" not in dxConstructorArguments:
      dxConstructorArguments["uzStatusCode"] = oSelf.__uStatusCode;
    if "sbzReasonPhrase" not in dxConstructorArguments:
      dxConstructorArguments["sbzReasonPhrase"] = oSelf.__sbReasonPhrase;
    # Add any required constructor arguments for a clone from the super class
    return super().fdxGetCloneConstructorArguments(**dxConstructorArguments);

  @property
  def uStatusCode(oSelf) -> int:
    return oSelf.__uStatusCode;
  @uStatusCode.setter
  def uStatusCode(oSelf,
    uStatusCode: int,
  ):
    fAssertTypes({
      "uStatusCode": (uStatusCode, int),
    });
    oSelf.__uStatusCode = uStatusCode;
  
  @property
  def sbReasonPhrase(oSelf) -> bytes:
    return oSelf.__sbReasonPhrase;
  @sbReasonPhrase.setter
  def sbReasonPhrase(oSelf,
    sbReasonPhrase: bytes,
  ): # setting to b"" will result in it being set to a common message for the current status code.
    fAssertTypes({
      "sbReasonPhrase": (sbReasonPhrase, bytes),
    });
    fAssertType("sbReasonPhrase", sbReasonPhrase, bytes);
    oSelf.__sbReasonPhrase = sbReasonPhrase or oSelf.fsbGetDefaultReasonPhraseForStatus(oSelf.__uStatusCode);
  
  def fsbGetStartLine(oSelf) -> bytes:
    return b"%s %d %s" % (oSelf.sbVersion, oSelf.__uStatusCode, oSelf.__sbReasonPhrase);
