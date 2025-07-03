from ..mExceptions import (
  cInvalidChunkBodyException,
  cInvalidChunkedDataException,
  cInvalidChunkHeaderException,
  cInvalidChunkSizeException,
  cInvalidTrailerException,
);
from ..mHeadersTrailers import cTrailers;

from .cChunk import cChunk;
from .cChunkHeader import cChunkHeader;

class cChunkedData(object):
  @classmethod
  def foFromChunksData(cClass, *,
    asbData: list[bytes],
    dxTrailers: dict = {},
  ):
    return cClass(
      aoChunks = [
        cChunk(sbData)
        for sbData in asbData
      ],
      oLastChunkHeader = cChunkHeader(
        uSize = 0,
      ),
      oTrailers = cTrailers.foFromDict(
        dxTrailers,
      ),
    );
  @classmethod
  def foDeserialize(cClass,
    sbData: bytes,
  ) -> "cChunkedData": # string to avoid self-reference before the class is defined
    # Make sure the data ends with CRLF:
    if sbData[-2:] != b"\r\n":
      raise cInvalidChunkBodyException(
        "The chunked data does not end with CRLF.",
        sbData = sbData[-2:],
      );
    sbData = sbData[:-2]; # Discard the ending CRLF
    aoChunks = [];
    while 1:
      try:
        (
          sbChunkHeader,
          sbData,
        ) = sbData.split(b"\r\n", 1);
      except ValueError:
        raise cInvalidChunkHeaderException(
          "The remaining data for chunk #%d does not contain a CRLF to mark the end of the chunk header." % (
            len(aoChunks) + 1,
          ),
          sbData = sbData,
        );
      oChunkHeader = cChunkHeader.foDeserialize(sbChunkHeader);
      if oChunkHeader.uSize == 0:
        oLastChunkHeader = oChunkHeader;
        break;
      if len(sbData) < oChunkHeader.uSize:
        raise cInvalidChunkSizeException(
          "The chunk size (%d) of chunk #%d is larger than the remaining data." % (
            oChunkHeader.uSize,
            len(aoChunks) + 1,
          ),
          sbData = sbData,
        );
      sbChunkData = sbData[:oChunkHeader.uSize];
      aoChunks.append(cChunk(
        sbData = sbChunkData,
        dsb0ExtensionValue_by_sbName = oChunkHeader.dsb0ExtensionValue_by_sbName,
      ));
      sbData = sbData[oChunkHeader.uSize:];
      if sbData[:2] != b"\r\n":
        raise cInvalidChunkBodyException(
          "The chunk body of chunk #%d does not end with CRLF." % (
            len(aoChunks) + 1,
          ),
          sbData = sbData[:2],
        );
      sbData = sbData[2:];
      # loop to parse next chunk
    if sbData:
      oTrailers = cTrailers.foDeserialize(sbData);
    else:
      oTrailers = cTrailers();
    return cClass(
      aoChunks = aoChunks,
      oLastChunkHeader = oLastChunkHeader,
      oTrailers = oTrailers,
    );
    

  def __init__(oSelf,
    *,
    aoChunks: cChunk,
    oLastChunkHeader: cChunkHeader,
    oTrailers: cTrailers,
  ):
    oSelf.aoChunks = aoChunks;
    oSelf.oLastChunkHeader = oLastChunkHeader;
    oSelf.oTrailers = oTrailers;
  
  @property
  def sbData(oSelf,
  ) -> bytes:
    # Return the concatenated data in all chunks as a bytes string.
    return b"".join([
      oChunk.sbData
      for oChunk in oSelf.aoChunks
    ]);
  
  def fsbSerialize(oSelf) -> bytes:
    sbChunks = b"".join(
      oChunk.fsbSerialize()
      for oChunk in oSelf.aoChunks
    );
    sbLastChunkHeader = oSelf.oLastChunkHeader.fsbSerialize();
    sbTrailers = oSelf.oTrailers.fsbSerialize();
    return sbChunks + sbLastChunkHeader + sbTrailers + b"\r\n";
