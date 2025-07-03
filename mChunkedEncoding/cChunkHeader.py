from ..mExceptions import cInvalidChunkSizeException;

class cChunkHeader(object):
  @classmethod
  def foDeserialize(cClass,
    sbChunkHeader: bytes,
  ) -> "cChunkHeader":
    asbChunkHeaderSizeAndExtensions = sbChunkHeader.split(b";");
    sbChunkSize = asbChunkHeaderSizeAndExtensions[0].strip();
    asbChunkExtensions = asbChunkHeaderSizeAndExtensions[1:];
    try:
      uChunkSize = int(sbChunkSize, 16);
    except ValueError:
      raise cInvalidChunkSizeException(
        "The chunk header size value %s is not a valid hex number" % sbChunkSize,
        sbData = sbChunkHeader,
      );
    dsb0ExtensionValue_by_sbName = {};
    for sbChunkExtension in asbChunkExtensions:
      asbNameAndOptionalValue = sbChunkExtension.split(b"=", 1);
      sbName = asbNameAndOptionalValue[0].strip();
      sb0Value = asbNameAndOptionalValue[1].strip() if len(asbNameAndOptionalValue) > 1 else None;
      dsb0ExtensionValue_by_sbName[sbName] = sb0Value;
    return cClass(
      uSize = uChunkSize,
      dsb0ExtensionValue_by_sbName = dsb0ExtensionValue_by_sbName,
    );
  
  def __init__(oSelf,
    uSize: int,
    dsb0ExtensionValue_by_sbName: dict[bytes, bytes | None] | None = {},
  ):
    oSelf.uSize = uSize;
    oSelf.dsb0ExtensionValue_by_sbName = dsb0ExtensionValue_by_sbName;

  def fsbSerialize(oSelf) -> bytes:
    sbChunkHeader = b"%X" % oSelf.uSize;
    if oSelf.dsb0ExtensionValue_by_sbName:
      sbChunkHeader += b"".join(
        b"; %s%s" % (sbName, b"=%s" % (sb0Value or b""))
        for (sbName, sb0Value) in oSelf.dsb0ExtensionValue_by_sbName.items()
      );
    return sbChunkHeader + b"\r\n";

