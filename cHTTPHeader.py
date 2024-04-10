from mNotProvided import fAssertType;

class cHTTPHeader(object):
  def __init__(oSelf, sbName, *tsbValueLines):
    oSelf.__sbLowerName = None;
    oSelf.__sbLowerValue = None;
    oSelf.__sbName = None;
    oSelf.__asbValueLines = None;
    oSelf.sbName = sbName;
    oSelf.asbValueLines = list(tsbValueLines);
  
  @property
  def sbName(oSelf):
    return oSelf.__sbName;
  
  @sbName.setter
  def sbName(oSelf, sbName):
    fAssertType("sbName", sbName, bytes);
    if sbName != oSelf.__sbName:
      oSelf.__sbName = sbName;
      oSelf.__sbLowerName = None;
  
  @property
  def sbLowerName(oSelf):
    if oSelf.__sbLowerName is None:
      oSelf.__sbLowerName = oSelf.sbName.lower();
    return oSelf.__sbLowerName;
  
  @property
  def asbValueLines(oSelf):
    return list(oSelf.__asbValueLines);
  
  @asbValueLines.setter
  def asbValueLines(oSelf, asbValueLines):
    oSelf.__asbValueLines = [];
    oSelf.fAddValueLines(asbValueLines);
  
  def fAddValueLines(oSelf, asbValueLines):
    fAssertType("asbValueLines", asbValueLines, [bytes]);
    for sbValueLine in asbValueLines:
      oSelf.fAddValueLine(sbValueLine);
  
  def fAddValueLine(oSelf, sbValueLine):
    fAssertType("sbValueLine", sbValueLine, bytes);
    assert len(sbValueLine) > 0, \
        "HTTP header values must contain a value";
    assert len(oSelf.__asbValueLines) == 0 or sbValueLine[0] in b" \t", \
        "HTTP header value lines after the first must start with whitespace, not %s" % repr(sbValueLine);
    oSelf.__asbValueLines.append(sbValueLine);
  
  @property
  def sbValue(oSelf):
    return b" ".join([
      sbValueLine.strip()
      for sbValueLine in oSelf.__asbValueLines
    ]);
  
  @sbValue.setter
  def sbValue(oSelf, sbValue):
    oSelf.__asbValueLines = [];
    oSelf.fAddValueLine(sbValue);
  
  @property
  def sbLowerValue(oSelf):
    if oSelf.__sbLowerValue is None:
      oSelf.__sbLowerValue = oSelf.sbValue.lower();
    return oSelf.__sbLowerValue;
  
  def foClone(oSelf):
    return oSelf.__class__(oSelf.__sbName, *oSelf.__asbValueLines);
  
  def fGet_dsbValue_by_sbName(oSelf):
    # Get the list of name-value pairs and convert them into a dictionary.
    return dict(oSelf.fGet_atsbName_and_sbValue());
  
  def fGet_atsbName_and_sbValue(oSelf):
    # Parse the value as a ';' separated list of name=value pairs and return
    # a list with (name, value) tuples.
    atsbName_and_sbValue = [];
    for sbNameAndValue in oSelf.sbValue.split(b";"):
      tsbValue_and_sbName = sbNameAndValue.split(b"=", 1);
      if len(tsbValue_and_sbName) == 2:
        (sbName, sbValue) = tsbValue_and_sbName;
        atsbName_and_sbValue.append((sbName.strip(), sbValue.strip()));
      else:
        (sbName,) = tsbValue_and_sbName;
        atsbName_and_sbValue.append((sbName.strip(), b""));
    return atsbName_and_sbValue;
  
  def fsb0GetNamedValue(oSelf, sbValueName):
    # Parse the value as a ';' separated list of name=value pairs, find the
    # named values in this list that matches the given name and return the
    # corresponding value for the last one found. Returns "" if this pair has
    # no value, and None if there is no such pair.
    sbStrippedLowerValueName = sbValueName.strip().lower();
    sb0Value = None; # Remains None of no matching name value pair is found.
    for (sbName, sbValue) in oSelf.fGet_atsbName_and_sbValue():
      if sbName.lower() == sbStrippedLowerValueName:
        sb0Value = sbValue; # return "" if it has no value.
    return sb0Value;
  
  def fasbGetHeaderLines(oSelf):
    asbHeaderLines = [b"%s: %s" % (oSelf.__sbName, oSelf.__asbValueLines[0])];
    if len(oSelf.__asbValueLines) > 1:
      asbHeaderLines += oSelf.__asbValueLines[1:];
    return asbHeaderLines;
  
  def fasGetDetails(oSelf):
    return [s for s in [
      str(b"%s:%s" % (oSelf.__sbName, b" ".join(oSelf.__asbValueLines)), "ascii", "strict"),
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));
