import re, urllib;
from .mHTTPExceptions import *;
from .fdsURLDecodedNameValuePairsFromString import fdsURLDecodedNameValuePairsFromString;
from .fsURLEncodedStringFromNameValuePairs import fsURLEncodedStringFromNameValuePairs;

gdtxDefaultPortAndSecure_by_sProtocol = {
  "http": (80, False),
  "https": (443, True),
};

UNSPECIFIED = {};

srIPv4Byte = ( # No support for octal encoding!
  "(?:"
    "25[0-5]"                        # 250-255
  "|"
    "2[0-4][0-9]"                    # 200-249
  "|"
    "[1][0-9]{2}"                    # 100-199
  "|"
    "[1-9][0-9]"                     # 10-99
  "|"
    "[0-9]"                          # 0-9
  ")"
);
srIPv4Address = "(?:" + srIPv4Byte + r"\." "){3}" + srIPv4Byte; # 0.1.2.3

srIPv6Word = "[0-9a-fA-F]{1,4}";
srIPv6PreWord = "(?:" + srIPv6Word + r"\:" ")";
srIPv6PostWord = "(?:" r"\:" + srIPv6Word + ")";
srIPv6Address = (
  r"\[" # IPv6 addresses are enclosed in "[" and "]" in URLs to avoid cofusion between "host:port" separator and "Word:word" separator
  "(?:" 
    + srIPv6Word              + srIPv6PostWord + "{7}"    # A:B:C:D:E:F:G:H
  "|"
    r"\:"                     + srIPv6PostWord + "{1,7}"  # ::B:C:D:E:F:G:H ... ::H
  "|"
    r"\:\:"                                               # ::
  "|"
    + srIPv6PreWord           + srIPv6PostWord + "{1,6}"  # A::C:D:E:F:G:H ... A::H
  "|"
    + srIPv6PreWord + "{2}"   + srIPv6PostWord + "{1,5}"  # A:B::D:E:F:G:H ... A:B::H
  "|"
    + srIPv6PreWord + "{3}"   + srIPv6PostWord + "{1,4}"  # A:B:C::E:F:G:H ... A:B:C::H
  "|"
    + srIPv6PreWord + "{4}"   + srIPv6PostWord + "{1,3}"  # A:B:C:D::F:G:H ... A:B:C:D::H
  "|"
    + srIPv6PreWord + "{5}"   + srIPv6PostWord + "{1,2}"  # A:B:C:D:E::G:H ... A:B:C:D:E::H
  "|"
    + srIPv6PreWord + "{6}"   + srIPv6PostWord +          # A:B:C:D:E:F::H
  "|"
    + srIPv6PreWord + "{0,7}" r"\:"                       # A:B:C:D:E:F:G:: ... A::
  "|" # ----------------------------
    "[Ff][Ee][89ab][0-9a-fA-F]" r"\:"     # (FE80-FEBF) ":" ... "%" local adapter
    # same as above, only we have a static first word, so "::..." options do not exist and repeat counts are different
    "(?:"
      + srIPv6Word              + srIPv6PostWord + "{6}"    # FExx:B:C:D:E:F:G:H
    "|"
      r"\:"                     + srIPv6PostWord + "{0,6}"  # FExx::C:D:E:F:G:H ... FExx::H, FExx::
    "|"
      + srIPv6PreWord + "{1}"   + srIPv6PostWord + "{1,5}"  # FExx:B::D:E:F:G:H ... FExx:B::H
    "|"
      + srIPv6PreWord + "{2}"   + srIPv6PostWord + "{1,4}"  # FExx:B:C::E:F:G:H ... FExx:B:C::H
    "|"
      + srIPv6PreWord + "{3}"   + srIPv6PostWord + "{1,3}"  # FExx:B:C:D::F:G:H ... FExx:B:C:D::H
    "|"
      + srIPv6PreWord + "{4}"   + srIPv6PostWord + "{1,2}"  # FExx:B:C:D:E::G:H ... FExx:B:C:D:E::H
    "|"
      + srIPv6PreWord + "{5}"   + srIPv6PostWord +          # FExx:B:C:D:E:F::H
    "|"
      + srIPv6PreWord + "{0,6}" r"\:"                       # FExx:B:C:D:E:F:G:: ... FExx::
    ")"                               #
    r"\%25" "[0-9a-zA-Z]+"            #   % is hex encoded as %25!
  "|" # ----------------------------
    "(?:"                             # ::ffff:<IPv4>, ::ffff:0:<IPv4>, and 64:ff9b::<IPv4>
      r"\:\:[Ff]{4}\:"                #
    "|"                               #
      r"\:\:[Ff]{4}\:0\:"             #
    "|"                               #
      r"64\:[Ff]{2}9[Bb]\:\:"         #
    ")"                               #
    + srIPv4Address +                 #
  ")" r"\]"
);
srDNSName = (
  r"[A-Za-z0-9]"            #     first char of hostname or lowest level domain name
  r"(?:"                    #     optional {
    r"[A-Za-z0-9\-]{0,61}"  #       second till second-to-last additional char of hostname or lowest level domain name
    r"[A-Za-z0-9]"          #       last additional char of hostname or lowest level domain name
  r")?"                     #     }
  r"(?:"                    #     optional { (for fully qualified domain names)
    r"\."                   #       "."
    r"(?:"                  #       repeat {
      r"[A-Za-z0-9]"        #         first char of intermediate level domain name
      r"(?:"                #         optional {
        r"[A-Za-z0-9\-]{0,61}" #        second till second-to-last additional char of intermediate level domain name
        r"[A-Za-z0-9]"      #           last additional char of intermediate level domain name
      r")?"                 #         }
      r"\."                 #         "."
    r")*"                   #       } any number of times
    r"[A-Za-z]{2,}"         #       top level domain name
  r")?"                     #     }
);

srProtocols = "|".join([re.escape(sProtocol) for sProtocol in gdtxDefaultPortAndSecure_by_sProtocol.keys()]);

rURL = re.compile(
  r"^"                        # {
  r"(" + srProtocols + ")://" #   (protocol) "://"
  r"("                        #   (either {
    + srIPv4Address +         #     IP v4
  r"|"                        #   } or {
    + srIPv6Address +         #     IP v6
  r"|"                        #   } or {
    + srDNSName +             #     DNS name
  r")"                        #   })
  r"(?:" r"\:(\d+)" r")?"     #   ":" (port)
  r"(\/[^#?]*)?"              #   optional { ("/" path) }
  r"(?:\?([^#]*))?"           #   optional { "?" (query) }
  r"(?:\#(.*))?"              #   optional { "#" (fragement) }
  r"$",                       # }
  re.I
);

class cURL(object):
  @staticmethod
  def foFromString(sURL):
    if isinstance(sURL, unicode):
      sURL = str(sURL);
    elif not isinstance(sURL, str):
      raise cInvalidURLException("Invalid URL", repr(sURL));
    oURLMatch = rURL.match(sURL);
    if not oURLMatch:
      raise cInvalidURLException("Invalid URL", sURL);
    (sProtocol, sHostname, szPort, szPath, szQuery, szFragment) = oURLMatch.groups();
    return cURL(sProtocol, sHostname, long(szPort) if szPort else None, szPath, szQuery, szFragment);
  
  # There is also a non-static version that allows relative URLs:
  def foFromRelativeString(oSelf, sURL, bMustBeRelative = False):
    if not isinstance(sURL, (str, unicode)):
      raise cInvalidURLException("Invalid relative URL", repr(sURL));
    oRelativeURLMatch = re.match("^(?:%s)$" % "".join([
      r"(\/?[^:#?]*)?",
      r"(?:\?([^#]*))?",
      r"(?:\#(.*))?",
    ]), sURL);
    if not oRelativeURLMatch:
      if bMustBeRelative:
        raise cInvalidURLException("Invalid relative URL", repr(sURL));
      return cURL.foFromString(sURL);
    (szPath, szQuery, szFragment) = oRelativeURLMatch.groups();
    if szPath and not szPath.startswith("/"):
      # Path is relative too
      szPath = "/" + "/".join(oSelf.asPath[:-1] + [szPath]);
    return oSelf.foClone(
      szPath = szPath or UNSPECIFIED,
      # specifying the path but not the query will remove the query
      szQuery = szQuery if szPath or szQuery else UNSPECIFIED,
      # specifying the path or query but not the fragment will remove the fragment
      szFragment = szFragment if szPath or szQuery or szFragment else UNSPECIFIED,
    );
  
  def __init__(oSelf, sProtocol, sHostname, uzPort = None, szPath = None, szQuery = None, szFragment = None):
    assert isinstance(sProtocol, str), \
        "sProtocol must be an sASCII string, not %s" % repr(sProtocol);
    assert isinstance(sHostname, str), \
        "sHostname must be an sASCII string, not %s" % repr(sHostname);
    assert uzPort is None or isinstance(uzPort, (int, long)), \
        "uzPort must be None, an int or a long, not %s" % repr(uzPort);
    assert szPath is None or isinstance(szPath, str), \
        "szPath must be None or an ASCII string, not %s" % repr(szPath);
    assert szQuery is None or isinstance(szQuery, str), \
        "szQuery must be None or an ASCII string, not %s" % repr(szQuery);
    assert szFragment is None or isinstance(szFragment, str), \
        "szFragment must be None or an ASCII string, not %s" % repr(szFragment);
    oSelf.__sProtocol = sProtocol;
    oSelf.__sHostname = sHostname;
    oSelf.__uzPort = uzPort;
    oSelf.sPath = szPath; # Use setter so we can reuse code that guarantees this starts with "/"
    oSelf.__szQuery = szQuery;
    oSelf.__szFragment = szFragment;
  
  def foClone(oSelf,
    szProtocol = UNSPECIFIED, szHostname = UNSPECIFIED, uzPort = UNSPECIFIED,
    szPath = UNSPECIFIED, szQuery = UNSPECIFIED, szFragment = UNSPECIFIED
  ):
    return cURL(
      sProtocol = szProtocol if szProtocol is not UNSPECIFIED else oSelf.__sProtocol,
      sHostname = szHostname if szHostname is not UNSPECIFIED else oSelf.__sHostname,
      uzPort = uzPort if uzPort is not UNSPECIFIED else oSelf.__uzPort,
      szPath = szPath if szPath is not UNSPECIFIED else oSelf.__sPath,
      szQuery = szQuery if szQuery is not UNSPECIFIED else oSelf.__szQuery,
      szFragment = szFragment if szFragment is not UNSPECIFIED else oSelf.__szFragment,
    );
  
  ### Protocol #################################################################
  @property
  def sProtocol(oSelf):
    return oSelf.__sProtocol;
  
  @property
  def bSecure(oSelf):
    return gdtxDefaultPortAndSecure_by_sProtocol[oSelf.__sProtocol][1];
  
  ### Hostname #################################################################
  @property
  def sHostname(oSelf):
    return oSelf.__sHostname;
  @sHostname.setter
  def sHostname(oSelf, sHostname):
    assert isinstance(sHostname, str), \
        "sHostname must be an sASCII string, not %s" % repr(sHostname);
    oSelf.__sHostname = sHostname;
  
  ### Port #####################################################################
  @property
  def uPort(oSelf):
    return oSelf.__uzPort if oSelf.__uzPort is not None else gdtxDefaultPortAndSecure_by_sProtocol[oSelf.__sProtocol][0];
  @property
  def uzPort(oSelf):
    return oSelf.__uzPort;
  @uzPort.setter
  def uzPort(oSelf, uzPort = None):
    assert uzPort is None or isinstance(uzPort, (int, long)), \
        "uzPort must be None, an int or a long, not %s" % repr(uzPort);
    oself.__uzPort = uzPort;
  
  ### Path #####################################################################
  @property
  def sURLDecodedPath(oSelf):
    return urllib.unquote(oSelf.__sPath);
  
  @property
  def sPath(oSelf):
    return oSelf.__sPath;
  @sPath.setter
  def sPath(oSelf, szPath):
    assert szPath is None or isinstance(szPath, str), \
        "szPath must be None an sASCII string, not %s" % repr(szPath);
    oSelf.__sPath = ("/" if (not szPath or szPath[0] != "/") else "") + (szPath or "");
  
  @property
  def asPath(oSelf):
    return oSelf.__sPath[1:].split("/") if oSelf.__sPath != "/" else [];
  @asPath.setter
  def asPath(oSelf, asPath):
    if asPath is None:
      oSelf.__sPath = "/";
    else:
      assert isinstance(asPath, list), \
          "asPath must be a list of strings, not %s" % repr(asPath);
      for sComponent in asPath:
        assert isinstance(sComponent, str), \
            "asPath must be a list of strings, not %s" % repr(asPath);
      oSelf.__sPath = "/" + "/".join(asPath);
  
  ### Query ####################################################################
  @property
  def szQuery(oSelf):
    return oSelf.__szQuery;
  @szQuery.setter
  def szQuery(oSelf, szQuery):
    assert szQuery is None or isinstance(szQuery, str), \
        "szQuery must be None or an sASCII string, not %s" % repr(szQuery);
    oSelf.__szQuery = szQuery;
  @property
  def dsQueryValue_by_sName(oSelf):
    return fdsURLDecodedNameValuePairsFromString(oSelf.__szQuery) if oSelf.__szQuery else {};
  @dsQueryValue_by_sName.setter
  def dsQueryValue_by_sName(oSelf, dzsQueryValue_by_sName):
    assert isinstance(dzsQueryValue_by_sName, dict), \
        "Invalid argument %s" % repr(dzsQueryValue_by_sName);
    oSelf.__szQuery = fsURLEncodedStringFromNameValuePairs(dzsQueryValue_by_sName);
  
  def fsGetQueryValue(oSelf, sName):
    return oSelf.dsQueryValue_by_sName.get(sName);
  
  def fSetQueryValue(oSelf, sName, sValue):
    dsQueryValue_by_sName = oSelf.dsQueryValue_by_sName;
    dsQueryValue_by_sName[sName] = sValue;
    oSelf.dsQueryValue_by_sName = dsQueryValue_by_sName;

  ### Fragment #################################################################
  @property
  def szFragment(oSelf):
    return oSelf.__szFragment;
  @szFragment.setter
  def szFragment(oSelf, szFragment):
    assert szFragment is None or isinstance(szFragment, str), \
        "szFragment must be None or an sASCII string, not %s" % repr(szFragment);
    oSelf.__szFragment = szFragment;
    
  ### Convenience ##############################################################
  @property
  def sAddress(oSelf):
    return "%s:%d" % (oSelf.__sHostname, oSelf.uPort);
  
  @property
  def sHostnameAndPort(oSelf):
    bNonDefaultPort = oSelf.__uzPort not in [None, gdtxDefaultPortAndSecure_by_sProtocol[oSelf.__sProtocol][0]];
    return oSelf.__sHostname + (":%d" % oSelf.__uzPort if bNonDefaultPort else "");
  
  @property
  def oBase(oSelf):
    return cURL(sProtocol = oSelf.__sProtocol, sHostname = oSelf.sHostname, uzPort = oSelf.__uzPort);
  
  @property
  def sBase(oSelf):
    return oSelf.__sProtocol + "://" + oSelf.sHostnameAndPort;
  
  @property
  def sRelative(oSelf):
    return "%s%s%s" % (
      oSelf.__sPath,
      ("?%s" % oSelf.__szQuery) if oSelf.__szQuery is not None else "",
      ("#%s" % oSelf.__szFragment) if oSelf.__szFragment is not None else "",
    );
  
  @property
  def sAbsolute(oSelf):
    return oSelf.sBase + oSelf.sRelative;
  def __str__(oSelf):
    return oSelf.sAbsolute;
  
  def fasDump(oSelf):
    return [
      "sProtocol: %s" % repr(oSelf.__sProtocol),
      "sHostname: %s" % repr(oSelf.__sHostname),
      "uzPort: %s" % repr(oSelf.__uzPort),
      "sPath: %s" % repr(oSelf.__sPath),
      "szQuery: %s" % repr(oSelf.__szQuery),
      "szFragment: %s" % repr(oSelf.__szFragment),
    ];
  
  def fsToString(oSelf):
    sDetails = oSelf.sAbsolute;
    return "%s{%s}" % (oSelf.__class__.__name__, sDetails);
