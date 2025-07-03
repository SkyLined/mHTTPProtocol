from .cChunkHeader import cChunkHeader;

from mNotProvided import fAssertType;

class cChunk(object):
  def __init__(oSelf,
    sbData: bytes,
    *,
    dsb0ExtensionValue_by_sbName: dict = {},
  ):
    fAssertType("sbData", sbData, bytes);
    oSelf.sbData = sbData;
    oSelf.dsb0ExtensionValue_by_sbName = dsb0ExtensionValue_by_sbName;
  
  def foGetHeader(oSelf) -> cChunkHeader:
    return cChunkHeader(
      uSize = len(oSelf.sbData),
      dsb0ExtensionValue_by_sbName = oSelf.dsb0ExtensionValue_by_sbName,
    );
  
  def fsbSerialize(oSelf) -> bytes:
    return (
      oSelf.foGetHeader().fsbSerialize() +
      oSelf.sbData + b"\r\n"
    );
  

