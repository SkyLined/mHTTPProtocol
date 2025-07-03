import re, urllib.parse;

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
  fxGetFirstProvidedValue,
  zNotProvided
);

from .cResponse import cResponse;
from .iMessage import iMessage;
from .mCompression import asbSupportedCompressionTypes;
from .mExceptions import *;
from .mHeadersTrailers import cHeaders;

gsbSupportedCompressionTypes= b", ".join(asbSupportedCompressionTypes);
gsbUserAgent = b"Mozilla/5.0 (compatible)";
grMethod = re.compile(b"^[A-Z]+$");

class cRequest(iMessage):
  ddDefaultHeader_sbValue_by_sbName_by_sbHTTPVersion = {
    b"HTTP/1.0": {
      b"Accept": b"*/*",
      b"Accept-Encoding": gsbSupportedCompressionTypes,
      b"Connection": b"Close",
      b"User-Agent": gsbUserAgent,
    },
    b"HTTP/1.1": {
      b"Accept": b"*/*",
      b"Accept-Encoding": gsbSupportedCompressionTypes,
      b"Cache-Control": b"No-Cache, Must-Revalidate",
      b"Connection": b"Keep-Alive",
      b"User-Agent": gsbUserAgent,
    },
  };
  bCanHaveBodyIfConnectionCloseHeaderIsPresent = False;
  
  @staticmethod
  @ShowDebugOutput
  def fdxDeserializeStartLine(
    sbStartLine: bytes,
  ) -> dict:
    fAssertTypes({
      "sbStartLine": (sbStartLine, bytes),
    });
    asbComponents = sbStartLine.split(b" ", 2);
    if len(asbComponents) != 3:
      raise cInvalidMessageException(
        "The request start line is invalid.",
        sbData = sbStartLine,
      );
    (sbMethod, sbURL, sbVersion) = asbComponents;
    if len(sbMethod) == 0:
      raise cInvalidMessageException(
        "The request start line does not contain a method.",
        sbData = sbStartLine,
      );
    
    if len(sbURL) == 0:
      raise cInvalidMessageException(
        "The request start line does not contain a URL.",
        sbData = sbStartLine,
      );
    
    if not sbVersion.startswith(b"HTTP/"):
      raise cInvalidMessageException(
        "The HTTP version in the request start line is invalid.",
        sbData = sbStartLine,
      );
    # Return value is a dict with elements that take the same name as their corresponding constructor arguments.
    return {
      "sbzMethod": sbMethod,
      "sbURL": sbURL,
      "sbzVersion": sbVersion,
    };
  
  @ShowDebugOutput
  def __init__(oSelf,
    sbURL: bytes,
    *,
    sbzMethod: bytes | type(zNotProvided) = zNotProvided,
    **dxMessageConstructorArguments,
  ):
    fAssertTypes({
      "sbURL": (sbURL, bytes),
      "sbzMethod": (sbzMethod, bytes, zNotProvided),
    });
    iMessage.__init__(oSelf, **dxMessageConstructorArguments);
    oSelf.__sbURL = sbURL;
    oSelf.__sbMethod = fxGetFirstProvidedValue(sbzMethod, b"POST" if len(oSelf.sbBody) > 0 else b"GET");
  
  @property
  def sbURL(oSelf) -> bytes:
    return oSelf.__sbURL;
  @sbURL.setter
  def sbURL(oSelf,
    sbURL: bytes,
  ):
    fAssertTypes({
      "sbURL": (sbURL, bytes),
    });
    oSelf.__sbURL = sbURL;
  
  @property
  def sbMethod(oSelf) -> bytes:
    return oSelf.__sbMethod;
  @sbMethod.setter
  def sbMethod(oSelf,
    sbMethod: bytes,
  ):
    fAssertTypes({
      "sbMethod": (sbMethod, bytes),
    });
    oSelf.__sbMethod = sbMethod;
  
  def fdxGetCloneConstructorArguments(oSelf, **dxOverwrittenConstructorArguments) -> dict:
    dxConstructorArguments = dict(dxOverwrittenConstructorArguments);
    # Add any required constructor arguments for a clone that have not been overwritten:
    if "sbURL" not in dxConstructorArguments:
      dxConstructorArguments["sbURL"] = oSelf.__sbURL;
    if "sbzMethod" not in dxConstructorArguments:
      dxConstructorArguments["sbzMethod"] = oSelf.__sbMethod;
    # Add any required constructor arguments for a clone from the super class
    return super().fdxGetCloneConstructorArguments(**dxConstructorArguments);
  
  def fsbGetStartLine(oSelf) -> bytes:
    if not hasattr(oSelf, "sbMethod") or not hasattr(oSelf, "sbURL") or not hasattr(oSelf, "sbVersion"):
      return b"<uninitialized>";
    return b"%s %s %s" % (oSelf.sbMethod, oSelf.sbURL, oSelf.sbVersion);
  
  @ShowDebugOutput
  def foCreateResponse(oSelf,
    sbzVersion: bytes | None | type(zNotProvided) = zNotProvided,
    uzStatusCode: int | None | type(zNotProvided) = zNotProvided,
    sbzReasonPhrase: bytes | None | type(zNotProvided) = zNotProvided,
    *,
    o0zHeaders: cHeaders | None | type(zNotProvided) = zNotProvided,
    sb0Body: bytes | None = None,
    bSetContentLengthHeader: bool = False,
  ) -> cResponse:
    fAssertTypes({
      "sbzVersion": (sbzVersion, bytes, zNotProvided),
      "uzStatusCode": (uzStatusCode, int, zNotProvided),
      "sbzReasonPhrase": (sbzReasonPhrase, bytes, zNotProvided),
      "o0zHeaders": (o0zHeaders, cHeaders, zNotProvided),
      "sb0Body": (sb0Body, None, bytes),
      "bSetContentLengthHeader": (bSetContentLengthHeader, bool),
    });
    oResponse = cResponse(
      sbzVersion = fxGetFirstProvidedValue(sbzVersion, oSelf.sbVersion),
      uzStatusCode = uzStatusCode,
      sbzReasonPhrase = sbzReasonPhrase,
      o0zHeaders = o0zHeaders,
      sbBody = sb0Body or b"",
      bSetContentLengthHeader = bSetContentLengthHeader,
    );
    return oResponse;
  
