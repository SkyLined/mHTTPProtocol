import zlib;

from ..mExceptions import cUnhandledCompressionTypeValueException;

def fsbCompressDataUsingCompressionType(
  sbData: bytes,
  sbCompressionType: bytes,
  u0CompressionLevel: int | None = None,
) -> bytes:
  sbLowerCompressionType = sbCompressionType.lower();
  uCompressionLevel = zlib.Z_DEFAULT_COMPRESSION if u0CompressionLevel is None else u0CompressionLevel;
  if sbLowerCompressionType == b"deflate":
    oCompressionObject = zlib.compressobj(uCompressionLevel, zlib.DEFLATED, -zlib.MAX_WBITS);
    return oCompressionObject.compress(sbData) + oCompressionObject.flush();
  elif sbLowerCompressionType in [b"gzip", b"x-gzip"]:
    oCompressionObject = zlib.compressobj(uCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS | 0x10);
    return oCompressionObject.compress(sbData) + oCompressionObject.flush();
  elif sbLowerCompressionType in [B"", b"identity"]:
    return sbData; # No compression.
  elif sbLowerCompressionType == b"zlib":
    oCompressionObject = zlib.compressobj(uCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS);
    return oCompressionObject.compress(sbData) + oCompressionObject.flush();
  else:
    raise cUnhandledCompressionTypeValueException(
      "Compression type %s is not handled" % repr(sbCompressionType)[1:],
      sbData = sbData,
      sbCompressionType = sbCompressionType,
    );

