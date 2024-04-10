import zlib;

guDeflateCompressionLevel = zlib.Z_DEFAULT_COMPRESSION;
guGZipCompressionLevel = zlib.Z_DEFAULT_COMPRESSION;
guZLibCompressionLevel = zlib.Z_DEFAULT_COMPRESSION;

def fsbCompressData(sbData, sbCompressionType):
  sbLowerCompressionType = sbCompressionType.lower();
  if sbLowerCompressionType == b"deflate":
    oCompressionObject = zlib.compressobj(guDeflateCompressionLevel, zlib.DEFLATED, -zlib.MAX_WBITS);
    return oCompressionObject.compress(sbData) + oCompressionObject.flush();
  elif sbLowerCompressionType in [b"gzip", b"x-gzip"]:
    oCompressionObject = zlib.compressobj(guGZipCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS | 0x10);
    return oCompressionObject.compress(sbData) + oCompressionObject.flush();
  elif sbLowerCompressionType in [B"", b"identity"]:
    return sbData; # No compression.
  elif sbLowerCompressionType == b"zlib":
    oCompressionObject = zlib.compressobj(guZLibCompressionLevel, zlib.DEFLATED, zlib.MAX_WBITS);
    return oCompressionObject.compress(sbData) + oCompressionObject.flush();
  else:
    raise NotImplementedError("%s encoding is not supported" % repr(sbCompressionType)[1:]);

fsbCompressData.asbSupportedCompressionTypes = [b"deflate", b"gzip", b"x-gzip", b"zlib"];