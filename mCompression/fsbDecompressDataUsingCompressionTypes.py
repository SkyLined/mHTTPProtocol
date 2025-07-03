from .fsbDecompressDataUsingCompressionType import fsbDecompressDataUsingCompressionType;

def fsbDecompressDataUsingCompressionTypes(
  *,
  sbData: bytes,
  asbCompressionTypes: list[bytes],
):
  for sbCompressionType in reversed(asbCompressionTypes):
    sbData = fsbDecompressDataUsingCompressionType(sbData, sbCompressionType);
  return sbData;
