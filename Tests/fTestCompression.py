
def fTestCompression():
  from fsbCompressData import fsbCompressData;
  from fsbDecompressData import fsbDecompressData;
  
  assert set(fsbCompressData.asbSupportedCompressionTypes) == set(fsbDecompressData.asbSupportedCompressionTypes), \
      "fsbCompressData does not support the same compression types as fsbDecompressData:\nfsbCompressData: %s\nfsbDecompressData: %s" % (
        repr(fsbCompressData.asbSupportedCompressionTypes),
        repr(fsbDecompressData.asbSupportedCompressionTypes),
      );
  
  sbData = bytes(x for x in range(0x100));
  
  for sCompressionType in fsbCompressData.asbSupportedCompressionTypes:
    sbCompressedData = fsbCompressData(sbData, sCompressionType);
    sbUncompressedData = fsbDecompressData(sbCompressedData, sCompressionType);
    assert sbData == sbUncompressedData, \
        "Compressing/decompressing data using %s resulted in different data!?\n%s\n%s" % (
          repr(sCompressionType),
          repr(sbData),
          repr(sbUncompressedData),
        );