import zlib;
from .mExceptions import cHTTPInvalidEncodedDataException;

def fsbDecompressData(sbData, sbCompressionType):
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
      raise cHTTPInvalidEncodedDataException(
        sMessage = "%s encoding is not supported" % (repr(sbCompressionType)[1:],),
        dxDetails = {
          "sbCompressionType": sbCompressionType,
          "sbData": sbData,
        },
      );
  except zlib.error as oException:
    raise cHTTPInvalidEncodedDataException(
      sMessage = "Invalid %s-encoded data%s" % (
        str(sbLowerCompressionType, "ascii", "strict"),
        ": %s" % oException.args[0] if oException.args else "",
      ),
      dxDetails = {
        "sbCompressionType": sbCompressionType,
        "sbData": sbData,
      },
    );

fsbDecompressData.asbSupportedCompressionTypes = [b"deflate", b"gzip", b"x-gzip", b"zlib"];