try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = fShowDebugOutput = lambda x: x; # NOP

from mNotProvided import *;

from .cHTTPHeader import cHTTPHeader;
from .mExceptions import *;

class cHTTPHeaders(object):
  @classmethod
  @ShowDebugOutput
  def foFromDict(cClass, dxHeaders):
    return cClass([cHTTPHeader(sbName, sbValue) for (sbName, sbValue) in dxHeaders.items()]);
  
  @ShowDebugOutput
  def __init__(oSelf, a0oHeaders = None):
    fAssertType("a0oHeaders", a0oHeaders, [cHTTPHeader], None);
    oSelf.__aoHeaders = a0oHeaders or [];
  
  def foClone(oSelf):
    return oSelf.__class__([oHeader.foClone() for oHeader in oSelf.__aoHeaders]);
  
  @property
  def uNumberOfHeaders(oSelf):
    return len(oSelf.__aoHeaders);
  
  def faoGetHeaders(oSelf):
    return oSelf.__aoHeaders[:];
  
  @ShowDebugOutput
  def faoGetHeadersForName(oSelf, sbName):
    fAssertType("sbName", sbName, bytes);
    sbLowerName = sbName.lower();
    return [oHeader for oHeader in oSelf.__aoHeaders if oHeader.sbLowerName == sbLowerName];
  
  @ShowDebugOutput
  def fo0GetUniqueHeaderForName(oSelf, sbName, o0AdditionalHeaders = None):
    # returns the first header with the given name.
    # will throw a cHTTPInvalidMessageException if there are multiple headers
    # with the given name with different values, ignoring case.
    aoHeaders = oSelf.faoGetHeadersForName(sbName);
    if o0AdditionalHeaders:
      aoHeaders += o0AdditionalHeaders.faoGetHeadersForName(sbName);
    if len(aoHeaders) == 0:
      return None;
    if len(aoHeaders) > 1:
      uNumberOfUniqueHeaderValues = len(set([oHeader.sbLowerValue for oHeader in aoHeaders]));
      if uNumberOfUniqueHeaderValues > 1:
        raise cHTTPInvalidMessageException(
          "A valid HTTP message cannot have more than 1 unique value for the %s header" % sbName,
          {"aoHeaders": aoHeaders},
        );
    return aoHeaders[0];
  
  def fAddHeader(oSelf, oHeader):
    fAssertType("oHeader", oHeader, cHTTPHeader);
    fShowDebugOutput("Adding %s:%s header." % (oHeader.sbName, b"\n".join(oHeader.asbValueLines)));
    oSelf.__aoHeaders.append(oHeader);
  
  def fbRemoveHeader(oSelf, oHeader):
    fAssertType("oHeader", oHeader, cHTTPHeader);
    if oHeader not in oSelf.__aoHeaders:
      return False;
    fShowDebugOutput("Removing %s:%s header." % (oHeader.sbName, "b\n".join(oHeader.asbValueLines)));
    oSelf.__aoHeaders.remove(oHeader);
    return True;
  
  def fbReplaceHeaders(oSelf, oHeader):
    fAssertType("oHeader", oHeader, cHTTPHeader);
    bReplaced = False;
    for oOldHeader in oSelf.__aoHeaders[:]:
      if oOldHeader.sbLowerName == oHeader.sbLowerName:
        oSelf.__aoHeaders.remove(oOldHeader);
        fShowDebugOutput("Removing %s:%s header." % (oOldHeader.sbName, b"\n".join(oOldHeader.asbValueLines)));
        bReplaced = True;
    fShowDebugOutput("Adding %s:%s header." % (oHeader.sbName, b"\n".join(oHeader.asbValueLines)));
    oSelf.__aoHeaders.append(oHeader);
    return bReplaced;
  
  def foAddHeaderForNameAndValue(oSelf, sbName, sbValue):
    fShowDebugOutput("Adding %s:%s header." % (sbName, sbValue));
    oSelf.__aoHeaders.append(cHTTPHeader(sbName, sbValue));
  
  @ShowDebugOutput
  def fbHasValueForName(oSelf, sbName, sb0Value = None):
    fAssertType("sbName", sbName, bytes);
    assert sb0Value is None or isinstance(sb0Value, bytes), \
        "sb0Value must be 'bytes' or 'None', not %s:%s" % (type(sb0Value), repr(sb0Value));
    sbLowerName = sbName.lower();
    sb0LowerValue = sb0Value.lower() if sb0Value is not None else None;
    for oHeader in oSelf.__aoHeaders:
      if oHeader.sbLowerName == sbLowerName:
        if sb0Value is None or oHeader.sbLowerValue == sb0LowerValue:
          fShowDebugOutput("Found %s:%s header." % (oHeader.sbName, b"\n".join(oHeader.asbValueLines)));
          return True;
    return False;
  
  @ShowDebugOutput
  def fbHasUniqueValueForName(oSelf, sbName, sbValue, o0AdditionalHeaders = None):
    # returns true if all headers with the given name have the provided value,
    # ignoring case.
    # will throw a cHTTPInvalidMessageException if there are multiple headers
    # with the given name with different values, ignoring case.
    fAssertType("sbName", sbName, bytes);
    fAssertType("sbValue", sbValue, bytes);
    fAssertType("o0AdditionalHeaders", o0AdditionalHeaders, cHTTPHeaders, None);
    o0Header = oSelf.fo0GetUniqueHeaderForName(sbName, o0AdditionalHeaders);
    if o0Header is None:
      fShowDebugOutput("No %s header found." % sbName);
      return False;
    oHeader = o0Header;
    if oHeader.sbLowerValue != sbValue.lower():
      fShowDebugOutput("Header value %s != %s" % (repr(oHeader.sbLowerValue), repr(sbValue.lower())));
      return False;
    fShowDebugOutput("Found %s:%s header." % (oHeader.sbName, b"\n".join(oHeader.asbValueLines)));
    return True;
  
  @ShowDebugOutput
  def fbRemoveHeadersForName(oSelf, sbName, sb0Value = None):
    fAssertType("sbName", sbName, bytes);
    fAssertType("sb0Value", sb0Value, bytes, None);
    sbLowerName = sbName.lower();
    sb0LowerValue = sb0Value.lower() if sb0Value is not None else None;
    bRemoved = False;
    for oOldHeader in oSelf.__aoHeaders[:]:
      if oOldHeader.sbLowerName == sbLowerName:
        if sb0Value is None or oOldHeader.sbLowerValue == sb0LowerValue:
          fShowDebugOutput("Removing %s:%s header." % (oOldHeader.sbName, b"\n".join(oOldHeader.asbValueLines)));
          oSelf.__aoHeaders.remove(oOldHeader);
          bRemoved = True;
    return bRemoved;
  
  @ShowDebugOutput
  def fbReplaceHeadersForNameAndValue(oSelf, sbName, sbValue):
    fAssertType("sbName", sbName, bytes);
    fAssertType("sbValue", sbValue, bytes);
    sbLowerName = sbName.lower();
    sbLowerValue = sbValue.lower();
    oExistingHeader = None;
    for oOldHeader in oSelf.__aoHeaders[:]:
      if oOldHeader.sbLowerName == sbLowerName:
        if oExistingHeader is None:
          oExistingHeader = oOldHeader;
        else:
          fShowDebugOutput("Removing %s:%s header." % (oOldHeader.sbName, b"\n".join(oOldHeader.asbValueLines)));
          oSelf.__aoHeaders.remove(oOldHeader);
    if oExistingHeader:
      bReplaced = oExistingHeader.sbLowerValue != sbLowerValue;
      if bReplaced:
        fShowDebugOutput("Replacing %s:%s header value with %s." % (sbName, oExistingHeader.sbValue, sbValue));
      oExistingHeader.sbValue = sbValue;
    else:
      fShowDebugOutput("Adding %s:%s header." % (sbName, sbValue));
      oSelf.__aoHeaders.append(cHTTPHeader(sbName, sbValue));
      bReplaced = False;
    return bReplaced;
  
  def fasbGetHeaderLines(oSelf):
    asbHeaderLines = [];
    for oHeader in oSelf.__aoHeaders:
      asbHeaderLines += oHeader.fasbGetHeaderLines();
    return asbHeaderLines;
  
  def fasGetDetails(oSelf):
    return [s for s in [
      "%d headers, %d lines" % (len(oSelf.__aoHeaders), len(oSelf.fasGetHeaderLines())),
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));
