import re, urllib;

from .fdsURLDecodedNameValuePairsFromString import fdsURLDecodedNameValuePairsFromString;
from .fsURLEncodedStringFromNameValuePairs import fsURLEncodedStringFromNameValuePairs;
from .mExceptions import *;
from .mNotProvided import *;

gdtxDefaultPortAndSecure_by_sProtocol = {
  "http": (80, False),
  "https": (443, True),
};

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
    (sProtocol, sHostname, s0Port, s0Path, s0Query, s0Fragment) = oURLMatch.groups();
    return cURL(sProtocol, sHostname, long(s0Port) if s0Port else None, s0Path, s0Query, s0Fragment);
  
  # There is also a non-static version that allows relative URLs:
  def foFromRelativeString(oSelf, sURL, bMustBeRelative = False):
    if not isinstance(sURL, (str, unicode)):
      raise cInvalidURLException("Invalid relative URL", repr(sURL));
    oRelativeURLMatch = re.match("^(?:%s)$" % "".join([
      r"(\/?[^:#?]*)?",
      r"(\?[^#]*)?",
      r"(\#.*)?",
    ]), sURL);
    if not oRelativeURLMatch:
      if bMustBeRelative:
        raise cInvalidURLException("Invalid relative URL", repr(sURL));
      return cURL.foFromString(sURL);
    (sPath, s0Query, s0Fragment) = oRelativeURLMatch.groups();
    szPath = (
      # If a path is provided that starts with "/", override the existing path in the clone.
      sPath if sPath[:1] == "/" else
      # If a path is provided that does not starts with "/", make it relative to the existing path in the clone.
      ("/".join([""] + oSelf.asPath[:-1] + [sPath])) if sPath else
      # If no path is provided, don't change the path in the clone.
      zNotProvided
    );
    szQuery = (
      # If a query is provided, it will override the existing query in the clone.
      s0Query[1:] if s0Query else 
      # If no query is provided, but a path is, the query will be removed in the clone
      None if fbIsProvided(szPath) else
      # If no query or path is provided, the clone will have the same query.
      zNotProvided
    );
    szFragment = (
      # If a fragment is provided, it will override the existing fragment in the clone.
      s0Fragment[1:] if s0Fragment else 
      # If no fragment is provided, but a path and/or query is, the fragment will be removed in the clone
      None if fbIsProvided(szPath) or fbIsProvided(szQuery) else
      # If no fragment, query or path is provided, the clone will have the same fragment.
      zNotProvided
    );
    return oSelf.foClone(
      s0zPath = szPath,
      s0zQuery = szQuery,
      s0zFragment = szFragment,
    );
  
  def __init__(oSelf, sProtocol, sHostname, u0Port = None, s0Path = None, s0Query = None, s0Fragment = None):
    assert isinstance(sProtocol, str), \
        "sProtocol must be an sASCII string, not %s" % repr(sProtocol);
    assert isinstance(sHostname, str), \
        "sHostname must be an sASCII string, not %s" % repr(sHostname);
    assert u0Port is None or isinstance(u0Port, (int, long)), \
        "u0Port must be None, an int or a long, not %s" % repr(u0Port);
    assert s0Path is None or isinstance(s0Path, str), \
        "s0Path must be None or an ASCII string, not %s" % repr(s0Path);
    assert s0Query is None or isinstance(s0Query, str), \
        "s0Query must be None or an ASCII string, not %s" % repr(s0Query);
    assert s0Fragment is None or isinstance(s0Fragment, str), \
        "s0Fragment must be None or an ASCII string, not %s" % repr(s0Fragment);
    oSelf.__sProtocol = sProtocol;
    oSelf.__sHostname = sHostname;
    oSelf.__u0Port = u0Port;
    oSelf.sPath = s0Path; # Use setter so we can reuse code that guarantees this starts with "/"
    oSelf.__s0Query = s0Query;
    oSelf.__s0Fragment = s0Fragment;
  
  def foClone(oSelf,
    # All these can be provided to create a modified clone of the URL. If they
    # are not provided, the value from the original is used instead.
    szProtocol = zNotProvided,
    szHostname = zNotProvided,
    u0zPort = zNotProvided,
    s0zPath = zNotProvided,
    s0zQuery = zNotProvided,
    s0zFragment = zNotProvided
  ):
    return cURL(
      sProtocol   = fxGetFirstProvidedValue(szProtocol, oSelf.__sProtocol),
      sHostname   = fxGetFirstProvidedValue(szHostname, oSelf.__sHostname),
      u0Port      = fxGetFirstProvidedValue(u0zPort, oSelf.__u0Port),
      s0Path      = fxGetFirstProvidedValue(s0zPath, oSelf.__sPath),
      s0Query     = fxGetFirstProvidedValue(s0zQuery, oSelf.__s0Query),
      s0Fragment  = fxGetFirstProvidedValue(s0zFragment, oSelf.__s0Fragment),
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
    return oSelf.__u0Port if oSelf.__u0Port is not None else gdtxDefaultPortAndSecure_by_sProtocol[oSelf.__sProtocol][0];
  @property
  def u0Port(oSelf):
    return oSelf.__u0Port;
  @u0Port.setter
  def u0Port(oSelf, u0Port = None):
    assert u0Port is None or isinstance(u0Port, (int, long)), \
        "u0Port must be None, an int or a long, not %s" % repr(u0Port);
    oself.__u0Port = u0Port;
  
  ### Path #####################################################################
  @property
  def sURLDecodedPath(oSelf):
    return urllib.unquote(oSelf.__sPath);
  
  @property
  def sPath(oSelf):
    return oSelf.__sPath;
  @sPath.setter
  def sPath(oSelf, s0Path):
    assert s0Path is None or isinstance(s0Path, str), \
        "s0Path must be None an sASCII string, not %s" % repr(s0Path);
    oSelf.__sPath = ("/" if (not s0Path or s0Path[0] != "/") else "") + (s0Path or "");
  
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
  def s0Query(oSelf):
    return oSelf.__s0Query;
  @s0Query.setter
  def s0Query(oSelf, s0Query):
    assert s0Query is None or isinstance(s0Query, str), \
        "s0Query must be None or an sASCII string, not %s" % repr(s0Query);
    oSelf.__s0Query = s0Query;
  @property
  def dsQueryValue_by_sName(oSelf):
    return fdsURLDecodedNameValuePairsFromString(oSelf.__s0Query) if oSelf.__s0Query else {};
  @dsQueryValue_by_sName.setter
  def dsQueryValue_by_sName(oSelf, d0sQueryValue_by_sName):
    assert isinstance(d0sQueryValue_by_sName, dict), \
        "Invalid argument %s" % repr(d0sQueryValue_by_sName);
    oSelf.__s0Query = fsURLEncodedStringFromNameValuePairs(d0sQueryValue_by_sName);
  
  def fs0GetQueryValue(oSelf, sName):
    return oSelf.dsQueryValue_by_sName.get(sName);
  
  def fSetQueryValue(oSelf, sName, sValue):
    dsQueryValue_by_sName = oSelf.dsQueryValue_by_sName;
    dsQueryValue_by_sName[sName] = sValue;
    oSelf.dsQueryValue_by_sName = dsQueryValue_by_sName;

  ### Fragment #################################################################
  @property
  def s0Fragment(oSelf):
    return oSelf.__s0Fragment;
  @s0Fragment.setter
  def s0Fragment(oSelf, s0Fragment):
    assert s0Fragment is None or isinstance(s0Fragment, str), \
        "s0Fragment must be None or an sASCII string, not %s" % repr(s0Fragment);
    oSelf.__s0Fragment = s0Fragment;
    
  ### Convenience ##############################################################
  @property
  def sAddress(oSelf):
    return "%s:%d" % (oSelf.__sHostname, oSelf.uPort);
  
  @property
  def sHostnameAndPort(oSelf):
    bNonDefaultPort = oSelf.__u0Port not in [None, gdtxDefaultPortAndSecure_by_sProtocol[oSelf.__sProtocol][0]];
    return oSelf.__sHostname + (":%d" % oSelf.__u0Port if bNonDefaultPort else "");
  
  @property
  def oBase(oSelf):
    return cURL(sProtocol = oSelf.__sProtocol, sHostname = oSelf.sHostname, u0Port = oSelf.__u0Port);
  
  @property
  def sBase(oSelf):
    return oSelf.__sProtocol + "://" + oSelf.sHostnameAndPort;
  
  @property
  def sRelative(oSelf):
    return "%s%s%s" % (
      oSelf.__sPath,
      ("?%s" % oSelf.__s0Query) if oSelf.__s0Query is not None else "",
      ("#%s" % oSelf.__s0Fragment) if oSelf.__s0Fragment is not None else "",
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
      "u0Port: %s" % repr(oSelf.__u0Port),
      "sPath: %s" % repr(oSelf.__sPath),
      "s0Query: %s" % repr(oSelf.__s0Query),
      "s0Fragment: %s" % repr(oSelf.__s0Fragment),
    ];
  
  def fsToString(oSelf):
    sDetails = oSelf.sAbsolute;
    return "%s{%s}" % (oSelf.__class__.__name__, sDetails);
