import base64, zlib;

def fsbDecompressData(sbData, sbCompressionType):
  sbLowerCompressionType = sbCompressionType.lower();
  if sbLowerCompressionType == b"deflate":
    return zlib.decompress(sbData, -zlib.MAX_WBITS);
  elif sbLowerCompressionType in [b"gzip", b"x-gzip"]:
    return zlib.decompress(sbData, zlib.MAX_WBITS | 0x10);
  elif sbLowerCompressionType == b"identity":
    return sbData; # No compression.
  elif sbLowerCompressionType == b"zlib":
    return zlib.decompress(sbData, zlib.MAX_WBITS);
  else:
    raise NotImplementedError("%s decompression is not supported" % repr(sbCompressionType)[1:]);

fsbDecompressData.asbSupportedCompressionTypes = [b"deflate", b"gzip", b"x-gzip", b"zlib"];