try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

from .iNamedValue import iNamedValue;
from .fsbNormalize import fsbNormalize;

class iNamedValues(object):
  sNamedValuesTypeName = None; # "headers" | "trailers"
  cNamedValueClass = NotImplemented; # cHeader | cTrailer
  cInvalidNamedValueException = NotImplemented; # cInvalidHeaderException | cInvalidTrailerException

  @classmethod
  @ShowDebugOutput
  def foDeserialize(cClass,
    sbData: bytes, # do not include the trailing empty line!
  ) -> "iNamedValues": # string to avoid self-reference before the class is defined
    asbLines = sbData.split(b"\r\n");
    assert asbLines[-1] == b"", \
        f"{cClass.__name__} lines data did not end with \"\r\n\": {repr(sbData)[-10:]}";
    asbLines.pop();
    return cClass.foDeserializeLines(asbLines);

  @classmethod
  @ShowDebugOutput
  def foDeserializeLines(cClass,
    asbLines: list[bytes], # do not include the trailing empty line!
  ) -> "iNamedValues": # string to avoid self-reference before the class is defined
    # Officially field names cannot be empty, but we'll allow it.
    # Field values can be empty according to section 3.2 Header fields
    # ref. https://www.rfc-editor.org/rfc/rfc7230.html#page-22
    # Line continuations are obsolete but we'll handle them anyway.
    # We'll go through the headers in reverse order, so we can store header
    # continuation lines in a list until we get to the header line to which
    # they belong and process all of them together.
    aoNamedValues = [];
    asbCurrentNamedValueLines = [];
    for sbLine in reversed(asbLines):
      asbCurrentNamedValueLines.insert(0, sbLine);
      if len(sbLine.strip()) == 0:
        raise cClass.cInvalidNamedValueException(
          f"The {cClass.sNamedValuesTypeName} line was empty.",
          sbData = b"".join(
            sbLine + b"\r\n"
            for sbLine in asbCurrentNamedValueLines
          ),
        );
      if sbLine[0] in b" \t":
        continue; # continuation line
      tsbNameAndFirstValueLine = sbLine.split(b":", 1);
      if len(tsbNameAndFirstValueLine) != 2:
        raise cClass.cInvalidNamedValueException(
          f"The {cClass.sNamedValuesTypeName} line did not contain a name and value separated by a colon.",
          sbData = b"".join(sbLine + b"\r\n" for sbLine in asbCurrentNamedValueLines),
        );
      (sbName, sbFirstValueLine) = tsbNameAndFirstValueLine;
      aoNamedValues.insert(
        0,
        cClass.cNamedValueClass(
          sbName,
          sbFirstValueLine,
          *asbCurrentNamedValueLines[1:],
        ),
      );
      asbCurrentNamedValueLines = [];
    if len(asbCurrentNamedValueLines) > 0:
      raise cClass.cInvalidNamedValueException(
        f"The first {cClass.sNamedValuesTypeName} line was a continuation, rather than a name:value line, which is not valid.",
        sbData = b"".join(sbLine + b"\r\n" for sbLine in asbCurrentNamedValueLines),
      );

    return cClass(aoNamedValues);

  @staticmethod
  def fbIsValidValue(
    sbData
  ) -> bool:
    # Values must not contain CR or LF characters and have at least one
    # non-whitespace character
    return (
              b"\r" not in sbString and
              b"\n" not in sbString and
              len(sbString.strip("")) > 0
            );
  
  @classmethod
  def foFromDict(cClass,
    dxNamedValues: dict[bytes, bytes],
  ) -> "iNamedValues":
    return cClass([
      cClass.cNamedValueClass(sbName, sbValue)
      for (sbName, sbValue) in dxNamedValues.items()
    ]);
  
  @ShowDebugOutput
  def __init__(oSelf,
    aoNamedValues: list[iNamedValue] | None = [], 
  ):
    oSelf.__aoNamedValues = aoNamedValues or [];
  
  def foClone(oSelf,
  ) -> "iNamedValues": # string to avoid self-reference before the class is defined
    return oSelf.__class__([
      oNamedValue.foClone()
      for oNamedValue in oSelf.__aoNamedValues
    ]);
  
  ## GET (INFORMATION ABOUT) HEADERS/TRAILERS ##################################
  @property
  def uNumberOfNamedValues(oSelf,
  ) -> int:
    return len(oSelf.__aoNamedValues);
  @property
  def uNumberOfLines(oSelf,
  ) -> int:
    return sum(
      oNamedValue.uNumberOfLines
      for oNamedValue in oSelf.__aoNamedValues
    );
  def faoGet(oSelf,
  ) -> list[iNamedValue]:
    return oSelf.__aoNamedValues[:];
  
  def fbHasValueForNormalizedName(oSelf,
    sbName: bytes,
  ) -> bool:
    sbNormalizedName = fsbNormalize(sbName);
    for oNamedValue in oSelf.__aoNamedValues:
      if oNamedValue.sbNormalizedName == sbNormalizedName:
        return True;
    return False;
  @ShowDebugOutput
  def faoGetForNormalizedName(oSelf,
    sbName: bytes,
  ) -> bool:
    # Returns all named value instances which' normalized name match the given
    # name.
    sbNormalizedName = fsbNormalize(sbName);
    return [
      oNamedValue for oNamedValue in oSelf.__aoNamedValues
      if oNamedValue.sbNormalizedName == sbNormalizedName
    ];
  @ShowDebugOutput
  def fasbGetUniqueNormalizedValuesForNormalizedName(oSelf,
    sbName: bytes,
  ) -> list[bytes]:
    # Returns all the normalized values for all named values which' normalized
    # name match the given name.
    return list(set([
      oNamedValue.sbNormalizedValue
      for oNamedValue in oSelf.faoGetForNormalizedName(sbName)
    ]));
  @ShowDebugOutput 
  def fbContainsNormalizedNameAndUniqueNormalizedValue(oSelf,
    *,
    sbName: bytes,
    sbValue: bytes,
  ) -> bool:
    # Returns True if there are named values which' normalized name match the
    # given name and all of which' normalized value matches the given value.
    sbNormalizedValue = fsbNormalize(sbValue);
    aoNamedValues = oSelf.faoGetForNormalizedName(sbName);
    for oNamedValue in aoNamedValues:
      if oNamedValue.sbNormalizedValue != sbNormalizedValue:
        fShowDebugOutput("Named value %s != %s" % (repr(oNamedValue.sbValue)[1:], repr(sbValue())[1:]));
        return False;
    fShowDebugOutput("Found %d named values." % (len(aoNamedValues),));
    return len(aoNamedValues) > 0;
  @ShowDebugOutput
  def fbHasCommaSeparatedValueForNormalizedName(oSelf,
    sbName: bytes,
    sbValue: bytes,
  ) -> bool:
    # Return True if there is at least one named value which' normalized name
    # matches the given name, and which has a comma-separated list of values
    # in which one of these normalized values matches the given value.
    aoNamedValues = oSelf.faoGetForNormalizedName(sbName);
    if len(aoNamedValues) == 0:
      fShowDebugOutput("No %s named values found." % (
        repr(sbName)[1:],
      ));
      return False;
    sbNormalizedValue = fsbNormalize(sbValue);
    for oNamedValue in aoNamedValues:
      for sbExistingValue in oNamedValue.asbCommaSeparatedValues:
        if sbNormalizedValue == fsbNormalize(sbExistingValue):
          fShowDebugOutput("Found named value %s: %s." % (
            repr(oNamedValue.sbName)[1:],
            repr(oNamedValue.sbValue)[1:],
          ));
          return True;
      fShowDebugOutput("The named value %s: %s does not contain %s" % (
        repr(oNamedValue.sbName)[1:],
        repr(oNamedValue.sbValue)[1:],
        repr(sbValue)[1:]
      ));
    return False;
  
  ## ADD HEADERS/TRAILERS ######################################################
  @ShowDebugOutput  
  def fAdd(oSelf,
    oNamedValue: iNamedValue,
  ):
    oSelf.__aoNamedValues.append(oNamedValue);
  @ShowDebugOutput
  def foAddNameAndValue(oSelf,
    sbName: bytes,
    sbValue: bytes,
  ) -> iNamedValue:
    oNamedValue = oSelf.cNamedValueClass(sbName, sbValue);
    oSelf.__aoNamedValues.append(oNamedValue);
    return oNamedValue;
  @ShowDebugOutput
  def foReplaceOrAddUniqueNameAndValue(oSelf,
    sbName: bytes,
    sbValue: bytes,
  ) -> iNamedValue:
    sbNormalizedValue = fsbNormalize(sbValue);
    aoExistingNamedValues = oSelf.faoGetForNormalizedName(sbName);
    o0FoundNamedValue = None;
    for oNamedValue in aoExistingNamedValues:
      if oNamedValue.sbNormalizedValue == sbNormalizedValue:
        if o0FoundNamedValue is not None:
          fShowDebugOutput("Removed named value %s: %s." % (
            repr(oNamedValue.sbName)[1:],
            repr(oNamedValue.sbValue)[1:],
          ));
          oSelf.fRemoveNamedValue(oNamedValue);
        else:
          o0FoundNamedValue = oNamedValue;
          if oNamedValue.sbValue != sbValue:
            oNamedValue.sbValue = sbValue;
            fShowDebugOutput("Updated NamedValue %s: %s." % (
              repr(oNamedValue.sbName)[1:],
              repr(oNamedValue.sbValue)[1:],
            ));
          else:
            fShowDebugOutput("Found NamedValue %s: %s." % (
              repr(oNamedValue.sbName)[1:],
              repr(oNamedValue.sbValue)[1:],
            ));
    if o0FoundNamedValue:
      return o0FoundNamedValue;
    oNamedValue = oSelf.cNamedValueClass(sbName, sbValue);
    oSelf.fAdd(oNamedValue);
    fShowDebugOutput("Added named value %s: %s." % (
      repr(oNamedValue.sbName)[1:],
      repr(oNamedValue.sbValue)[1:],
    ));
    return oNamedValue;
  @ShowDebugOutput
  def fReplaceOrAddUniqueCommaSeparatedValueForNormalizedName(oSelf,
    sbName: bytes,
    sbValue: bytes,
  ):
    sbNormalizedValue = fsbNormalize(sbValue);
    aoNamedValues = oSelf.faoGetForNormalizedName(sbName);
    bFoundValue = False;
    for oNamedValue in aoNamedValues:
      fShowDebugOutput("Reviewing named value %s: %s." % (
        repr(oNamedValue.sbName)[1:],
        repr(oNamedValue.sbValue)[1:],
      ));
      asbNamedValueValues = oNamedValue.asbCommaSeparatedValues;
      asbUpdatedValues = [];
      bFoundValueInThisNamedValue = False;
      for sbExistingValue in asbNamedValueValues:
        if fsbNormalize(sbExistingValue) == sbNormalizedValue:
          if not bFoundValueInThisNamedValue:
            bFoundValueInThisNamedValue = True;
            fShowDebugOutput("Found value %s in named value %s: %s." % (
              repr(sbValue),
              repr(oNamedValue.sbName)[1:],
              repr(oNamedValue.sbValue)[1:],
            ));
            if not bFoundValue:
              bFoundValue = True; 
              # replace the first value with the unnormalized one
              asbUpdatedValues.append(sbValue);
            # else remove value from list.
        else:
          asbUpdatedValues.append(sbExistingValue);
      if not bFoundValueInThisNamedValue:
        fShowDebugOutput("The named value %s: %s does not contain %s" % (
          repr(oNamedValue.sbName)[1:],
          repr(oNamedValue.sbValue)[1:],
          repr(sbValue)[1:]
        ));
      elif len(asbUpdatedValues) == 0:
        fShowDebugOutput("Removed named value %s: %s." % (
          repr(oNamedValue.sbName)[1:],
          repr(oNamedValue.sbValue)[1:],
        ));
        oNamedValues.fRemoveNamedValue(oNamedValue);
      elif asbNamedValueValues != asbUpdatedValues:
        oNamedValue.sbValue = b", ".join(asbUpdatedValues);
        fShowDebugOutput("Updated named value %s: %s." % (
          repr(oNamedValue.sbName)[1:],
          repr(oNamedValue.sbValue)[1:],
        ));
    if not bFoundValue:
      # We haven't found an existing value; add it.
      oSelf.foAddNameAndValue(sbName, sbValue);
  ## REMOVE HEADERS/TRAILERS ###################################################
  @ShowDebugOutput
  def fRemove(oSelf,
    oNamedValue: iNamedValue,
  ):
    oSelf.__aoNamedValues.remove(oNamedValue);
  @ShowDebugOutput
  def fbRemoveForNormalizedName(oSelf,
    sbName: bytes,
  ) -> bool:
    sbNormalizedName = fsbNormalize(sbName);
    bRemoved = False;
    for oNamedValue in oSelf.__aoNamedValues[:]:
      if oNamedValue.sbNormalizedName == sbNormalizedName:
        fShowDebugOutput("Removing named value %s:%s." % (
          repr(oNamedValue.sbName)[1:],
          repr(oNamedValue.sbValue)[1:],
        ));
        oSelf.__aoNamedValues.remove(oNamedValue);
        bRemoved = True;
    return bRemoved;
  def fbRemoveForNormalizedNameAndValue(oSelf,
    sbName: bytes,
    sbValue: bytes,
  ) -> bool:
    sbNormalizedName = fsbNormalize(sbName);
    sbNormalizedValue = fsbNormalize(sbValue);
    bRemoved = False;
    for oNamedValue in oSelf.__aoNamedValues[:]:
      if oNamedValue.sbNormalizedName == sbNormalizedName:
        if oNamedValue.sbNormalizedValue == sb0NormalizedValue:
          fShowDebugOutput("Removing named value %s:%s." % (
            repr(oNamedValue.sbName)[1:],
            repr(oNamedValue.sbValue)[1:],
          ));
          oSelf.__aoNamedValues.remove(oNamedValue);
          bRemoved = True;
    return bRemoved;
  @ShowDebugOutput
  def fbRemoveCommaSeparatedValueForNormalizedName(oSelf,
    sbName: bytes,
    sbValue: bytes,
  ) -> bool:
    sbNormalizedValue = fsbNormalize(sbValue);
    aoNamedValues = oSelf.faoGetForNormalizedName(sbName);
    bRemoved = False;
    for oNamedValue in aoNamedValues:
      fShowDebugOutput("Reviewing named value %s: %s." % (
        repr(oNamedValue.sbName)[1:],
        repr(oNamedValue.sbValue)[1:],
      ));
      asbExistingValues = oNamedValue.asbCommaSeparatedValues;
      asbUpdatedValues = [
        sbExistingValue
        for sbExistingValue in asbExistingValues
        if fsbNormalize(sbExistingValue) != sbNormalizedValue
      ];
      if len(asbUpdatedValues) == 0:
        bRemoved = True;
        fShowDebugOutput("Removed named value %s: %s." % (
          repr(oNamedValue.sbName)[1:],
          repr(oNamedValue.sbValue)[1:],
        ));
        oSelf.fRemove(oNamedValue);
      elif asbExistingValues != asbUpdatedValues:
        bRemoved = True;
        oNamedValue.sbValue = b", ".join(asbUpdatedValues);
        fShowDebugOutput("Updated named value %s: %s." % (
          repr(oNamedValue.sbName)[1:],
          repr(oNamedValue.sbValue)[1:],
        ));
    return bRemoved;
  
  def fsbSerialize(oSelf) -> bytes:
    return b"".join([
      oNamedValue.fsbSerialize()
      for oNamedValue in oSelf.__aoNamedValues
    ]);
  
  def fasGetDetails(oSelf) -> list[str]:
    return [s for s in [
      "%d %s, %d lines" % (
        oSelf.uNumberOfNamedValues,
        oSelf.sNamedValuesTypeName,
        oSelf.uNumberOfLines
      ),
    ] if s];
  
  def __repr__(oSelf) -> str:
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf) -> str:
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));
