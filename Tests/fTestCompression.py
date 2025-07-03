
def fTestCompression(bRunFullTests):
  from mHTTPProtocol.mCompression import (
    asbSupportedCompressionTypes,
    fsbCompressDataUsingCompressionType,
    fsbCompressDataUsingCompressionTypes,
    fsbDecompressDataUsingCompressionType,
    fsbDecompressDataUsingCompressionTypes,
    ftxDecompressDataUsingExpectedCompressionTypesAndGetActualCompressionTypes,
  );
  
  sbData = bytes(x for x in range(0x100));
  
  for sbCompressionType in asbSupportedCompressionTypes:
    sbCompressedData = fsbCompressDataUsingCompressionType(
      sbData = sbData,
      sbCompressionType = sbCompressionType,
    );
    sbDecompressedData = fsbDecompressDataUsingCompressionType(
      sbData = sbCompressedData,
      sbCompressionType = sbCompressionType,
    );
    assert sbData == sbDecompressedData, \
        "Compressing/decompressing data using %s resulted in different data!?\n%s\n%s" % (
          repr(sCompressionType)[1:],
          repr(sbData)[1:],
          repr(sbDecompressedData)[1:],
        );
  sbCompressedData = fsbCompressDataUsingCompressionTypes(
    sbData = sbData,
    asbCompressionTypes = asbSupportedCompressionTypes,
  );
  sbDecompressedData = fsbDecompressDataUsingCompressionTypes(
    sbData = sbCompressedData,
    asbCompressionTypes = asbSupportedCompressionTypes,
  );
  assert sbData == sbDecompressedData, \
      "Compressing/decompressing data using %s resulted in different data!?\n%s\n%s" % (
        "/".join([
          repr(sbCompressionType)[1:]
          for sbCompressionType in asbSupportedCompressionTypes
        ]),
        repr(sbData)[1:],
        repr(sbDecompressedData)[1:],
      );
  
  (sbDecompressedData, asbActualCompressionTypes) = ftxDecompressDataUsingExpectedCompressionTypesAndGetActualCompressionTypes(
    sbData = sbCompressedData,
    asbExpectedCompressionTypes = [],
    bDataCanBeMoreCompressed = True,
  );
  assert sbData == sbDecompressedData, \
      "Compressing/decompressing data without knowing compression resulted in different data!?\n%s\n%s" % (
        repr(sbData)[1:],
        repr(sbDecompressedData)[1:],
      );
  assert sbData == sbDecompressedData, \
      "Compressing/decompressing data without knowing compression resulted in different compression types!?\n%s\n%s" % (
        "/".join([
          repr(sbCompressionType)[1:]
          for sbCompressionType in asbSupportedCompressionTypes
        ]),
        "/".join([
          repr(sbCompressionType)[1:]
          for sbCompressionType in asbActualCompressionTypes
        ]),
      );
