from .fsbNormalize import fsbNormalize;

class iNamedValue(object):
  sTypeName = None;
  cInvalidNamedValueException = NotImplemented;

  @classmethod
  def foDeserialize(cClass,
    sbData: bytes,
  ) -> "iNamedValue": # string to avoid self-reference before the class is defined
    asbLines = sbData.split(b"\r\n");
    if asbLines.pop() != b"":
      raise cClass.cInvalidNamedValueException(
        f"The {cClass.sTypeName} data did not end with CRLF.",
        sbData = sbData,
      );
    tsbNameAndFirstValueLine = asbLines.pop().split(b":", 1);
    if len(tsbNameAndFirstValueLine) != 2:
      raise cClass.cInvalidNamedValueException(
        f"The {cClass.sTypeName} line did not contain a name and value separated by a colon.",
        sbData = sbData,
      );
    (sbName, sbFirstValueLine) = tsbNameAndFirstValueLine;
    asbValueLines.insert(0, sbFirstValueLine);
    return cClass(
      sbName = sbName,
      tsbValueLines = asbValueLines,
    );

  def __init__(oSelf,
    sbName: bytes,
    *tsbValueLines
  ):
    oSelf.sbName = sbName;
    oSelf.__asbValueLines = None;
    oSelf.asbValueLines = list(tsbValueLines);
  
  def foClone(oSelf,
  ) -> "iNamedValue": # string to avoid self-reference before the class is defined
    return oSelf.__class__(oSelf.__sbName, *oSelf.__asbValueLines);
  
  ## NAME ######################################################################
  @property
  def sbName(oSelf
  ) -> bytes:
    return oSelf.__sbName;
  
  @sbName.setter
  def sbName(oSelf,
    sbName: bytes,
  ):
    oSelf.__sbName = sbName;
    oSelf.__sbNormalizedName = fsbNormalize(sbName);
  
  @property
  def sbNormalizedName(oSelf
  ) -> bytes:
    return oSelf.__sbNormalizedName;
  
  ## VALUE LINES ###############################################################
  @property
  def uNumberOfLines(oSelf) -> int:
    return len(oSelf.__asbValueLines);
  @property
  def asbValueLines(oSelf,
  ) -> list[bytes]:
    return list(oSelf.__asbValueLines);
  
  @asbValueLines.setter
  def asbValueLines(oSelf,
    asbValueLines: list[bytes],
  ):
    oSelf.__asbValueLines = asbValueLines[:];
  
  ## VALUE #####################################################################
  @property
  def sbValue(oSelf,
  ) -> bytes:
    return b" ".join([
      sbValueLine.strip()
      for sbValueLine in oSelf.__asbValueLines
    ]);
  
  @sbValue.setter
  def sbValue(oSelf,
    sbValue: bytes,
  ):
    oSelf.__asbValueLines = [sbValue];
  
  @property
  def sbNormalizedValue(oSelf,
  ) -> bytes:
    return fsbNormalize(oSelf.sbValue);
  
  ## COMMA SEPARATED VALUES ####################################################
  @property
  def asbCommaSeparatedValues(oSelf,
  ) -> list[bytes]:
    return oSelf.sbValue.split(b",");
  @asbCommaSeparatedValues.setter
  def asbCommaSeparatedValues(oSelf,
    asbCommaSeparatedValues: list[bytes],
  ):
    oSelf.sbValue = b", ".join(asbCommaSeparatedValues);
  
  def fbHasNormalizedCommaSeparatedValue(oSelf,
    sbValue: bytes,
  ) -> bool:
    sbNormalizedValue = fsbNormalize(sbValue);
    for sbCommaSeparatedValue in oSelf.asbCommaSeparatedValues:
      if sbNormalizedValue == fsbNormalize(sbCommaSeparatedValue):
        return True;
    return False;

  ## SEMI-COLON SEPARATED PARAMETERS PAIRS #####################################
  @property
  def atsbParameterName_and_sb0Value(oSelf,
  ) -> tuple[bytes, bytes | None]:
    atsbName_and_sb0Value = [];
    iParametersStartIndex = oSelf.sbValue.find(b";");
    if iParametersStartIndex != -1:
      asUnparsedData = oSelf.sbValue[iParametersStartIndex + 1:].strip();
      while asUnparsedData:
        iNameEndIndex = 0;
        while iNameEndIndex < len(asUnparsedData) and asUnparsedData[iNameEndIndex] not in b"=;":
          iNameEndIndex += 1;
        bHasValue = asUnparsedData[iNameEndIndex:1] == "=";
        sbName = asUnparsedData[:iNameEndIndex].strip();
        asUnparsedData = asUnparsedData[iNameEndIndex + 1:].strip();
        if bHasValue:
          if asUnparsedData[:1] == '"':
            # quoted string; remove escapes and look for end.
            sbValue = b"";
            asUnparsedData = asUnparsedData[1:];
            while asUnparsedData and asUnparsedData[0] != '"':
              if asUnparsedData[0] == "\\":
                # escaped character; skip the backslash
                sbValue += asUnparsedData[1:1];
                asUnparsedData = asUnparsedData[2:];
              else:
                sbValue += asUnparsedData[0];
                asUnparsedData = asUnparsedData[1:];
            asUnparsedData = asUnparsedData[1:];  # skip the closing quote
          else:
            iValueEndIndex = asUnparsedData.find(b";");
            if iValueEndIndex == -1:
              sb0Value = asUnparsedData.strip();
              asUnparsedData = b"";
            else:
              sb0Value = asUnparsedData[:iValueEndIndex].strip();
              asUnparsedData = asUnparsedData[iValueEndIndex + 1:].strip();
        else:
          sb0Value = None;
        atsbName_and_sb0Value.append((sbName, sb0Value));
    return atsbName_and_sb0Value;
  
  def fsb0GetParameterValueForNormalizedName(oSelf,
    sbName: bytes,
  ) -> bytes | None:
    sbNormalizedName = fsbNormalize(sbName);
    # Returns the normalized value of the parameter with the given name.
    for (sbParameterName, sb0Value) in oSelf.atsbParameterName_and_sb0Value:
      if fsbNormalize(sbParameterName) == sbNormalizedName:
        return sb0Value;
    return None;
  
  def fsbSerialize(oSelf) -> bytes:
    sbValueLines = b"".join([
      b"%s\r\n" % sbLine
      for sbLine in oSelf.__asbValueLines
    ]);
    return b"%s: %s" % (oSelf.__sbName, sbValueLines);
  
  def fasGetDetails(oSelf) -> list[str]:
    return [s for s in [
      str(b"%s:%s" % (oSelf.__sbName, b"<CR><LF>".join(oSelf.__asbValueLines)), "ascii", "strict"),
    ] if s];
  
  def __repr__(oSelf) -> str:
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf) -> str:
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));

