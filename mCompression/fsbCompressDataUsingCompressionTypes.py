from .fsbCompressDataUsingCompressionType import fsbCompressDataUsingCompressionType;

def fsbCompressDataUsingCompressionTypes(
  *,
  sbData: bytes,
  asbCompressionTypes: list[bytes],
) -> bytes:
  for sbCompressionType in asbCompressionTypes:
    sbData = fsbCompressDataUsingCompressionType(
      sbData,
      sbCompressionType,
    );
  return sbData;
