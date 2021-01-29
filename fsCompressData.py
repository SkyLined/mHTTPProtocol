import base64, zlib;

try:
  from .cBrotli import cBrotli;
except Exception:
  cBrotli = None;

def fsCompressData(sData, sCompressionType):
  sLowerCompressionType = sCompressionType.lower();
  if cBrotli and sLowerCompressionType == "br":
    return cBrotli().compress(sData, guBrotliCompressionQuality);
  elif sLowerCompressionType == "deflate":
    oCompressionObject = zlib.compressobj(guDeflateCompressionLevel, zlib.DEFLATED, -zlib.MAX_WBITS);
    return oCompressionObject.compress(sData) + oCompressionObject.flush();
  elif sLowerCompressionType in ["gzip", "x-gzip"]:
    oCompressionObject = zlib.compressobj(guGZipCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS | 0x10);
    return oCompressionObject.compress(sData) + oCompressionObject.flush();
  elif sLowerCompressionType == "identity":
    return sData; # No compression.
  elif sLowerCompressionType == "zlib":
    oCompressionObject = zlib.compressobj(guZLibCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS);
    return oCompressionObject.compress(sData) + oCompressionObject.flush();
  else:
    raise NotImplementedError("Content encoding %s is not supported" % sEncodingType);

fsCompressData.asSupportedCompressionTypes = ["deflate", "gzip", "x-gzip", "zlib"] + (["br"] if cBrotli else []);