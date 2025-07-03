import zlib;

from ..mExceptions import (
  cInvalidCompressedDataException,
  cUnhandledCompressionTypeValueException,
);

def fsbDecompressDataUsingCompressionType(sbData, sbCompressionType):
  sbLowerCompressionType = sbCompressionType.lower();
  try:
    if sbLowerCompressionType == b"deflate":
      return zlib.decompress(sbData, -zlib.MAX_WBITS);
    elif sbLowerCompressionType in [b"gzip", b"x-gzip"]:
      return zlib.decompress(sbData, zlib.MAX_WBITS | 0x10);
    elif sbLowerCompressionType in [b"", b"identity"]:
      return sbData; # No compression.
    elif sbLowerCompressionType == b"zlib":
      return zlib.decompress(sbData, zlib.MAX_WBITS);
    else:
      raise cUnhandledCompressionTypeValueException(
        "Compression type %s is not handled" % repr(sbCompressionType)[1:],
        sbCompressionType = sbCompressionType,
        sbData = sbData,
      );
  except zlib.error as oException:
    raise cInvalidCompressedDataException(
      "Invalid %s-compressed data%s" % (
        repr(sbLowerCompressionType)[1:],
        ": %s" % oException.args[0] if oException.args else "",
      ),
      sbData = sbData,
      sbCompressionType = sbCompressionType,
    );
