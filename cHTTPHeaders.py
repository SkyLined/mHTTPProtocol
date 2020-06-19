try: # mDebugOutput use is Optional
  from mDebugOutput import *;
except: # Do nothing if not available.
  ShowDebugOutput = lambda fxFunction: fxFunction;
  fShowDebugOutput = lambda sMessage: None;
  fEnableDebugOutputForModule = lambda mModule: None;
  fEnableDebugOutputForClass = lambda cClass: None;
  fEnableAllDebugOutput = lambda: None;
  cCallStack = fTerminateWithException = fTerminateWithConsoleOutput = None;

from .mHTTPExceptions import *;
from .cHTTPHeader import cHTTPHeader;

class cHTTPHeaders(object):
  __ddDefaultHeader_sValue_by_sName_by_sHTTPVersion = {
    "HTTP/1.0": {
      "Connection": "Close",
      "Cache-Control": "No-Cache, Must-Revalidate",
      "Expires": "Wed, 16 May 2012 04:01:53 GMT", # 1337
      "Oragma": "No-Cache",
    },
    "HTTP/1.1": {
      "Connection": "Keep-Alive",
      "Cache-Control": "No-Cache, Must-Revalidate",
      "Expires": "Wed, 16 May 2012 04:01:53 GMT", # 1337
      "Pragma": "No-Cache",
    },
  };

  @classmethod
  @ShowDebugOutput
  def foDefaultHeadersForVersion(cClass, sVersion):
    dDefaultHeader_sValue_by_sName = cClass.__ddDefaultHeader_sValue_by_sName_by_sHTTPVersion.get(sVersion);
    assert dDefaultHeader_sValue_by_sName, \
        "Invalid HTTP version %s" % sVersion;
    return cClass.foFromDict(dDefaultHeader_sValue_by_sName);
  
  @classmethod
  @ShowDebugOutput
  def foFromDict(cClass, dxHeaders):
    return cClass([cHTTPHeader(sName, sValue) for (sName, sValue) in dxHeaders.items()]);
  
  @ShowDebugOutput
  def __init__(oSelf, aoHeaders = None):
    for oHeader in (aoHeaders or []):
      assert isinstance(oHeader, cHTTPHeader), \
          "aoHeaders must contain only cHTTPHeader instances, not %s" % repr(oHeader);
    oSelf.__aoHeaders = aoHeaders or [];
  
  def foClone(oSelf):
    return oSelf.__class__([oHeader.foClone() for oHeader in oSelf.__aoHeaders]);
  
  @property
  def uNumberOfHeaders(oSelf):
    return len(oSelf.__aoHeaders);
  
  def faoGetHeaders(oSelf):
    return oSelf.__aoHeaders[:];
  
  @ShowDebugOutput
  def faoGetHeadersForName(oSelf, sName):
    assert isinstance(sName, str), \
        "sName must be a string, not %s" % repr(sName);
    sLowerName = sName.lower();
    return [oHeader for oHeader in oSelf.__aoHeaders if oHeader.sLowerName == sLowerName];
  
  @ShowDebugOutput
  def fozGetUniqueHeaderForName(oSelf, sName, oAdditionalHeaders = None):
    # returns the first header with the given name.
    # will throw a cInvalidMessageException if there are multiple headers
    # with the given name with different values, ignoring case.
    aoHeaders = oSelf.faoGetHeadersForName(sName);
    if oAdditionalHeaders:
      aoHeaders += oAdditionalHeaders.faoGetHeadersForName(sName);
    if len(aoHeaders) == 0:
      return None;
    if len(aoHeaders) > 1:
      uNumberOfUniqueHeaderValues = len(set([oHeader.sLowerValue for oHeader in aoHeaders]));
      if uNumberOfUniqueHeaderValues > 1:
        raise cInvalidMessageException(
          "A valid HTTP message cannot have more than 1 unique value for the %s header" % sName,
          aoHeaders
        );
    return aoHeaders[0];
  
  def fAddHeader(oSelf, oHeader):
    assert isinstance(oHeader, cHTTPHeader), \
        "oHeader must be a cHTTPHeader instance, not %s" % repr(oHeader);
    fShowDebugOutput("Adding %s:%s header." % (oHeader.sName, "\n".join(oHeader.asValueLines)));
    oSelf.__aoHeaders.append(oHeader);
  
  def fbRemoveHeader(oSelf, oHeader):
    assert isinstance(oHeader, cHTTPHeader), \
        "oHeader must be a cHTTPHeader instance, not %s" % repr(oHeader);
    if oHeader not in oSelf.__aoHeaders:
      return False;
    fShowDebugOutput("Removing %s:%s header." % (oHeader.sName, "\n".join(oHeader.asValueLines)));
    oSelf.__aoHeaders.remove(oHeader);
    return True;
  
  def fbReplaceHeaders(oSelf, oHeader):
    assert isinstance(oHeader, cHTTPHeader), \
        "oHeader must be a cHTTPHeader instance, not %s" % repr(oHeader);
    bReplaced = False;
    for oOldHeader in oSelf.__aoHeaders[:]:
      if oOldHeader.sLowerName == oHeader.sLowerName:
        oSelf.__aoHeaders.remove(oOldHeader);
        fShowDebugOutput("Removing %s:%s header." % (oOldHeader.sName, "\n".join(oOldHeader.asValueLines)));
        bReplaced = True;
    fShowDebugOutput("Adding %s:%s header." % (oHeader.sName, "\n".join(oHeader.asValueLines)));
    oSelf.__aoHeaders.append(oHeader);
    return bReplaced;
  
  def foAddHeaderForNameAndValue(oSelf, sName, sValue):
    fShowDebugOutput("Adding %s:%s header." % (sName, sValue));
    oSelf.__aoHeaders.append(cHTTPHeader(sName, (" " if sValue[:1] != " " else "") + sValue));
  
  @ShowDebugOutput
  def fbHasValueForName(oSelf, sName, sValue = None):
    assert isinstance(sName, str), \
        "sName must be a string, not %s" % repr(sName);
    assert sValue is None or isinstance(sValue, str), \
        "sValue must be a string or None, not %s" % repr(sValue);
    sLowerName = sName.lower();
    sLowerValue = sValue.lower() if sValue is not None else None;
    for oHeader in oSelf.__aoHeaders:
      if oHeader.sLowerName == sLowerName:
        if sValue is None or oHeader.sLowerValue == sLowerValue:
          fShowDebugOutput("Found %s:%s header." % (oHeader.sName, "\n".join(oHeader.asValueLines)));
          return True;
    return False;
  
  @ShowDebugOutput
  def fbHasUniqueValueForName(oSelf, sName, sValue, oAdditionalHeaders = None):
    # returns true if all headers with the given name have the provided value,
    # ignoring case.
    # will throw a cInvalidMessageException if there are multiple headers
    # with the given name with different values, ignoring case.
    assert isinstance(sName, str), \
        "sName must be a string, not %s" % repr(sName);
    assert isinstance(sValue, str), \
        "sValue must be a string, not %s" % repr(sValue);
    ozHeader = oSelf.fozGetUniqueHeaderForName(sName, oAdditionalHeaders);
    if ozHeader is None:
      fShowDebugOutput("No %s header found." % sName);
      return False;
    if ozHeader.sLowerValue != sValue.lower():
      fShowDebugOutput("Header value %s != %s" % (repr(ozHeader.sLowerValue), repr(sValue.lower())));
      return False;
    fShowDebugOutput("Found %s:%s header." % (ozHeader.sName, "\n".join(ozHeader.asValueLines)));
    return True;
  
  @ShowDebugOutput
  def fbRemoveHeadersForName(oSelf, sName, sValue = None):
    assert isinstance(sName, str), \
        "sName must be a string, not %s" % repr(sName);
    assert sValue is None or isinstance(sValue, str), \
        "sValue must be a string or None, not %s" % repr(sValue);
    sLowerName = sName.lower();
    sLowerValue = sValue.lower() if sValue is not None else None;
    bRemoved = False;
    for oOldHeader in oSelf.__aoHeaders[:]:
      if oOldHeader.sLowerName == sLowerName:
        if sValue is None or oOldHeader.sLowerValue == sLowerValue:
          fShowDebugOutput("Removing %s:%s header." % (oOldHeader.sName, "\n".join(oOldHeader.asValueLines)));
          oSelf.__aoHeaders.remove(oOldHeader);
          bRemoved = True;
    return bRemoved;
  
  @ShowDebugOutput
  def fbReplaceHeadersForName(oSelf, sName, sValue):
    assert isinstance(sName, str), \
        "sName must be a string, not %s" % repr(sName);
    assert isinstance(sValue, str), \
        "sValue must be a string, not %s" % repr(sValue);
    sLowerName = sName.lower();
    sLowerValue = sValue.lower();
    oExistingHeader = None;
    for oOldHeader in oSelf.__aoHeaders[:]:
      if oOldHeader.sLowerName == sLowerName:
        if oExistingHeader is None:
          oExistingHeader = oOldHeader;
        else:
          fShowDebugOutput("Removing %s:%s header." % (oOldHeader.sName, "\n".join(oOldHeader.asValueLines)));
          oSelf.__aoHeaders.remove(oOldHeader);
    if oExistingHeader:
      bReplaced = oExistingHeader.sLowerValue != sLowerValue;
      if bReplaced:
        fShowDebugOutput("Replacing %s:%s header value with %s." % (sName, oExistingHeader.sValue, sValue));
      oExistingHeader.sValue = (" " if sValue[:1] != " " else "") + sValue;
    else:
      fShowDebugOutput("Adding %s:%s header." % (sName, sValue));
      oSelf.__aoHeaders.append(cHTTPHeader(sName, (" " if sValue[:1] != " " else "") + sValue));
      bReplaced = False;
    return bReplaced;
  
  def fasGetHeaderLines(oSelf):
    asHeaderLines = [];
    for oHeader in oSelf.__aoHeaders:
      asHeaderLines += oHeader.fasGetHeaderLines();
    return asHeaderLines;
  
  def fasGetDetails(oSelf):
    return [s for s in [
      "%d headers, %d lines" % (len(oSelf.__aoHeaders), len(oSelf.fasGetHeaderLines())),
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));
