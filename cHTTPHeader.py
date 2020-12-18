try: # mDebugOutput use is Optional
  from mDebugOutput import *;
except: # Do nothing if not available.
  ShowDebugOutput = lambda fxFunction: fxFunction;
  fShowDebugOutput = lambda sMessage: None;
  fEnableDebugOutputForModule = lambda mModule: None;
  fEnableDebugOutputForClass = lambda cClass: None;
  fEnableAllDebugOutput = lambda: None;
  cCallStack = fTerminateWithException = fTerminateWithConsoleOutput = None;

class cHTTPHeader(object):
  def __init__(oSelf, sName, *tsValueLines):
    oSelf.__sLowerStippedName = None;
    oSelf.__sLowerStippedValue = None;
    oSelf.__sName = None;
    oSelf.__asValueLines = None;
    oSelf.sName = sName;
    oSelf.asValueLines = list(tsValueLines);
  
  @property
  def sName(oSelf):
    return oSelf.__sName.strip();
  
  @sName.setter
  def sName(oSelf, sName):
    assert isinstance(sName, str), \
        "HTTP header names must be strings, not %s" % repr(sName);
    if sName != oSelf.__sName:
      oSelf.__sName = sName;
      oSelf.__sLowerName = None;
  
  @property
  def sLowerName(oSelf):
    if oSelf.__sLowerStippedName is None:
      oSelf.__sLowerStippedName = oSelf.sName.lower();
    return oSelf.__sLowerStippedName;
  
  @property
  def asValueLines(oSelf):
    return list(oSelf.__asValueLines);
  
  @asValueLines.setter
  def asValueLines(oSelf, asValueLines):
    oSelf.__asValueLines = [];
    oSelf.fAddValueLines(asValueLines);
  
  def fAddValueLines(oSelf, asValueLines):
    assert isinstance(asValueLines, list), \
        "asValueLines must be a list of strings, not %s" % repr(asValueLines);
    for sValueLine in asValueLines:
      oSelf.fAddValueLine(sValueLine);
  
  def fAddValueLine(oSelf, sValueLine):
    assert isinstance(sValueLine, str), \
        "HTTP header values must be strings, not %s" % repr(sValueLine);
    assert len(sValueLine.strip()) > 0, \
        "HTTP header values must contain a value, not %s" % repr(sValueLine);
    assert len(oSelf.__asValueLines) == 0 or sValueLine[0] in " \t", \
        "HTTP header value lines after the first must start with whitespace, not %s" % repr(sValueLine);
    oSelf.__asValueLines.append(sValueLine);
  
  @property
  def sValue(oSelf):
    return " ".join([
      sValueLine.strip()
      for sValueLine in oSelf.__asValueLines
    ]);
  
  @sValue.setter
  def sValue(oSelf, sValue):
    oSelf.__asValueLines = [];
    oSelf.fAddValueLine(sValue);
  
  @property
  def sLowerValue(oSelf):
    if oSelf.__sLowerStippedValue is None:
      oSelf.__sLowerStippedValue = oSelf.sValue.lower();
    return oSelf.__sLowerStippedValue;
  
  def foClone(oSelf):
    return oSelf.__class__(oSelf.__sName, *oSelf.__asValueLines);
  
  def fs0GetNamedValue(oSelf, sValueName):
    # Look through the named values after the first ';' from last to first.
    # Return as soon as one is seen; this will return the last value in the header.
    sLowerValueName = sValueName.lower();
    for sNameValuePair in reversed(oSelf.sLowerValue.split(";")[1:]):
      tsNameValuePair = sNameValuePair.split("=", 1);
      if len(tsNameValuePair) == 2:
        sName, sValue = tsNameValuePair;
        if sName.strip().lower() == sLowerValueName:
          return sValue;
    return None;
  
  def fasGetHeaderLines(oSelf):
    asHeaderLines = ["%s:%s" % (oSelf.__sName, oSelf.__asValueLines[0])];
    if len(oSelf.__asValueLines) > 1:
      asHeaderLines += oSelf.__asValueLines[1:];
    return asHeaderLines;

  def fasGetDetails(oSelf):
    return [s for s in [
      "%s:%s" % (oSelf.__sName, "\n".join(oSelf.__asValueLines)),
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));
