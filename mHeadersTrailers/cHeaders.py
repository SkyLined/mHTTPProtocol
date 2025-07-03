
from ..mExceptions import cInvalidHeaderException;

from .cHeader import cHeader;
from .iNamedValues import iNamedValues;

class cHeaders(iNamedValues):
  sNamedValuesTypeName = "headers";
  cNamedValueClass = cHeader;
  cInvalidNamedValueException = cInvalidHeaderException;
  
  def __init__(oSelf, aoHeaders: list[cHeader] | None = []):
    iNamedValues.__init__(oSelf, aoNamedValues = aoHeaders);
  
  @property
  def uNumberOfHeaders(oSelf) -> int:
    return oSelf.uNumberOfNamedValues;

  def fu0GetContentLength(oSelf, u0MaxValue: int | None = None) -> int | None:
    aoContentLengthHeaders = oSelf.faoGetForNormalizedName(b"Content-Length");
    # If there are none, we return None
    if len(aoContentLengthHeaders) == 0:
      return None;
    # If there are multiple we ignore all but the last one
    oContentLengthHeader = aoContentLengthHeaders[0];
    try:
      uContentLength = int(oContentLengthHeader.sbValue);
      if uContentLength < 0:
        raise ValueError();
    except ValueError:
      raise cInvalidMessageException(
        f"The {repr(oContentLengthHeader.sbName)[1:]} header value {repr(oContentLengthHeader.sbValue)[1:]} is invalid.",
      );
    if u0MaxValue is not None and uContentLength > u0MaxValue:
      raise cInvalidMessageException(
        f"The {repr(oContentLengthHeader.sbName)[1:]} header value {repr(oContentLengthHeader.sbValue)[1:]} is too large.",
      );
    return uContentLength;
