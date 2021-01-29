import base64, zlib;

try:
  from .cBrotli import cBrotli;
except Exception:
  cBrotli = None;

def fsDecompressData(sData, sCompressionType):
  sLowerCompressionType = sCompressionType.lower();
  if cBrotli and sLowerCompressionType == "br":
    return str(cBrotli().decompress(sData));
  elif sLowerCompressionType == "deflate":
    return zlib.decompress(sData, -zlib.MAX_WBITS);
  elif sLowerCompressionType in ["gzip", "x-gzip"]:
    return zlib.decompress(sData, zlib.MAX_WBITS | 0x10);
  elif sLowerCompressionType == "identity":
    return sData; # No compression.
  elif sLowerCompressionType == "zlib":
    return zlib.decompress(sData, zlib.MAX_WBITS);
  else:
    raise NotImplementedError("'%s' decompression is not supported" % sCompressionType);

fsDecompressData.asSupportedCompressionTypes = ["deflate", "gzip", "x-gzip", "zlib"] + (["br"] if cBrotli else []);