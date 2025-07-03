from ..mExceptions import cInvalidCompressedDataException;

from .asbSupportedCompressionTypes import asbSupportedCompressionTypes;
from .fsbDecompressDataUsingCompressionType import fsbDecompressDataUsingCompressionType;

def ftxDecompressDataUsingExpectedCompressionTypesAndGetActualCompressionTypes(
  *,
  sbData: bytes,
  asbExpectedCompressionTypes: list[bytes],
  # If the number of applied compression types may be wrong, setting
  # bDataCanBeLessCompressed to True will allow the function to return the data
  # even if the number of actual compressions is less than the number of
  # expected compressions.
  bDataCanBeLessCompressed: bool = False,
  # Similarly, setting bDataCanBeMoreCompressed to True will cause the code to
  # attempt to decompress the data with all known compression types until it
  # cannot be decompressed any further.
  bDataCanBeMoreCompressed: bool = False,
):
  asb0ActualCompressionTypes = [];
  for sbExpectedCompressionType in reversed(asbExpectedCompressionTypes):
    sbExpectedLowerCompressionType = sbExpectedCompressionType.lower();
    if sbExpectedLowerCompressionType == b"identity":
      asb0ActualCompressionTypes.append(b"identity");
      continue; # No compression.
    try:
      sbData = fsbDecompressDataUsingCompressionType(sbData, sbExpectedCompressionType);
    except cInvalidCompressedDataException:
      # The expected compression didn't work; try everything else we know:
      for sbCompressionType in asbSupportedCompressionTypes:
        if sbCompressionType is sbExpectedCompressionType:
          continue; # we already tried this.
        try:
          sbData = fsbDecompressData(sbData, sbCompressionType);
        except cInvalidCompressedDataException:
          pass; # This also doesn't work.
        except:
          # This works; add it to the list and continue the outer for loop
          asb0ActualCompressionTypes.append(sbCompressionType);
          break;
      else:
        # We tried all the supported compression types and none of them worked.
        if bDataCanBeLessCompressed:
          # The data can be less compressed than expected, but that is
          # acceptable, so return the data:
          return (sbData, asb0ActualCompressionTypes);
        # This is an error; re-raise it.
        raise;
  if not bDataCanBeMoreCompressed:
    return (sbData, asb0ActualCompressionTypes);
  # The data may be more compressed than the expected compression types imply.
  # Try to decompress the data with every known compression type until we cannot
  # decompress it any further:
  while 1:
    for sbCompressionType in asbSupportedCompressionTypes:
      try:
        sbData = fsbDecompressDataUsingCompressionType(sbData, sbCompressionType);
      except cInvalidCompressedDataException:
        continue; # That didn't work: try the next, if any.
      asb0ActualCompressionTypes.append(sbCompressionType);
      break;
    else:
      # We cannot decompress it further, so return the data:
      return (sbData, asb0ActualCompressionTypes);
