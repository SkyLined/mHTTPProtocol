
from ..mExceptions import cInvalidTrailerException;

from .cTrailer import cTrailer;
from .iNamedValues import iNamedValues;

class cTrailers(iNamedValues):
  sNamedValuesTypeName = "trailers";
  cNamedValueClass = cTrailer;
  cInvalidNamedValueException = cInvalidTrailerException;
  
  def __init__(oSelf, aoTrailers: list[cTrailer] | None = []):
    iNamedValues.__init__(oSelf, aoNamedValues = aoTrailers);
  
  @property
  def uNumberOfTrailers(oSelf) -> int:
    return oSelf.uNumberOfNamedValues;
