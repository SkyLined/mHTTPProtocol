from ..mExceptions import cInvalidTrailerException;

from .iNamedValue import iNamedValue;

class cTrailer(iNamedValue):
  cInvalidDataException = cInvalidTrailerException;
  sTypeName = "trailer";
