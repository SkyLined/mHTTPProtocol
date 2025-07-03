from ..mExceptions import cInvalidHeaderException;

from .iNamedValue import iNamedValue;

class cHeader(iNamedValue):
  cInvalidDataException = cInvalidHeaderException;
  sTypeName = "header";
