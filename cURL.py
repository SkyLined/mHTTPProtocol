import re, urllib.parse;

from mNotProvided import fAssertType, fbIsProvided, fxGetFirstProvidedValue, zNotProvided;

from .fdsURLDecodedNameValuePairsFromBytesString import fdsURLDecodedNameValuePairsFromBytesString;
from .fsbURLEncodedNameValuePairsToBytesString import fsbURLEncodedNameValuePairsToBytesString;
from .mExceptions import cHTTPInvalidURLException, acExceptions;

gdtxDefaultPortAndSecure_by_sbProtocol = {
  b"http": (80, False),
  b"https": (443, True),
};

gsbIPv4ByteRegExp = ( # No support for octal encoding!
  rb"(?:"
    rb"25[0-5]"                        # 250-255
  rb"|"
    rb"2[0-4][0-9]"                    # 200-249
  rb"|"
    rb"[1][0-9]{2}"                    # 100-199
  rb"|"
    rb"[1-9][0-9]"                     # 10-99
  rb"|"
    rb"[0-9]"                          # 0-9
  rb")"
);
gsbIPv4AddressRegExp   = rb"(?:" + gsbIPv4ByteRegExp + rb"\." rb"){3}" + gsbIPv4ByteRegExp; # 0.1.2.3

gsbIPv6WordRegExp      = rb"[0-9a-fA-F]{1,4}";
gsbIPv6PreWordRegExp   = rb"(?:" + gsbIPv6WordRegExp + rb"\:" rb")";
gsbIPv6PostWordRegExp   = rb"(?:" rb"\:" + gsbIPv6WordRegExp + rb")";
gsbIPv6AddressRegExp = (
  rb"(?:" 
    + gsbIPv6WordRegExp               + gsbIPv6PostWordRegExp + rb"{7}"      # A:B:C:D:E:F:G:H
  rb"|"
    rb"\:"                            + gsbIPv6PostWordRegExp + rb"{1,7}"    # ::B:C:D:E:F:G:H ... ::H
  rb"|"
    rb"\:\:"                                                                 # ::
  rb"|"
    + gsbIPv6PreWordRegExp            + gsbIPv6PostWordRegExp + rb"{1,6}"    # A::C:D:E:F:G:H ... A::H
  rb"|"
    + gsbIPv6PreWordRegExp + rb"{2}"  + gsbIPv6PostWordRegExp + rb"{1,5}"    # A:B::D:E:F:G:H ... A:B::H
  rb"|"
    + gsbIPv6PreWordRegExp + rb"{3}"  + gsbIPv6PostWordRegExp + rb"{1,4}"    # A:B:C::E:F:G:H ... A:B:C::H
  rb"|"
    + gsbIPv6PreWordRegExp + rb"{4}"  + gsbIPv6PostWordRegExp + rb"{1,3}"    # A:B:C:D::F:G:H ... A:B:C:D::H
  rb"|"
    + gsbIPv6PreWordRegExp + rb"{5}"  + gsbIPv6PostWordRegExp + rb"{1,2}"    # A:B:C:D:E::G:H ... A:B:C:D:E::H
  rb"|"
    + gsbIPv6PreWordRegExp + rb"{6}"  + gsbIPv6PostWordRegExp +              # A:B:C:D:E:F::H
  rb"|"
    + gsbIPv6PreWordRegExp + rb"{0,7}" rb"\:"                                # A:B:C:D:E:F:G:: ... A::
  rb"|" # ----------------------------
    rb"[Ff][Ee][89AaBb][0-9a-fA-F]" rb"\:"                          # (FE80-FEBF) ":" ... "%" local adapter
    # same as above, only we have a static first word, so "::..." options do not exist and repeat counts are different
    rb"(?:"
      + gsbIPv6WordRegExp               + gsbIPv6PostWordRegExp + rb"{6}"    # FExx:B:C:D:E:F:G:H
    rb"|"
                                        + gsbIPv6PostWordRegExp + rb"{1,6}"  # FExx::C:D:E:F:G:H ... FExx::H
    rb"|"
      rb"\:"                                                                 # FExx::
    rb"|"
      + gsbIPv6PreWordRegExp + rb"{1}"  + gsbIPv6PostWordRegExp + rb"{1,5}"  # FExx:B::D:E:F:G:H ... FExx:B::H
    rb"|"
      + gsbIPv6PreWordRegExp + rb"{2}"  + gsbIPv6PostWordRegExp + rb"{1,4}"  # FExx:B:C::E:F:G:H ... FExx:B:C::H
    rb"|"
      + gsbIPv6PreWordRegExp + rb"{3}"  + gsbIPv6PostWordRegExp + rb"{1,3}"  # FExx:B:C:D::F:G:H ... FExx:B:C:D::H
    rb"|"
      + gsbIPv6PreWordRegExp + rb"{4}"  + gsbIPv6PostWordRegExp + rb"{1,2}"  # FExx:B:C:D:E::G:H ... FExx:B:C:D:E::H
    rb"|"
      + gsbIPv6PreWordRegExp + rb"{5}"  + gsbIPv6PostWordRegExp +            # FExx:B:C:D:E:F::H
    rb"|"
      + gsbIPv6PreWordRegExp + rb"{0,6}" rb"\:"                              # FExx:B:C:D:E:F:G:: ... FExx::
    rb")"
    rb"\%25" rb"[0-9a-zA-Z]+"                                                #   % is hex encoded as %25!
  rb"|" # ----------------------------
    rb"(?:"                             # ::ffff:<IPv4>, ::ffff:0:<IPv4>, and 64:ff9b::<IPv4>
      rb"\:\:[Ff]{4}\:"                 #
    rb"|"                               #
      rb"\:\:[Ff]{4}\:0\:"              #
    rb"|"                               #
      rb"64\:[Ff]{2}9[Bb]\:\:"          #
    rb")"                               #
    + gsbIPv4AddressRegExp +            #
  rb")"
);
gsbDNSNameRegExp = (
  rb"[A-Za-z0-9]"               # first char of hostname or lowest level domain name
  rb"(?:"                       # optional {
    rb"[A-Za-z0-9\-]{0,61}"     #   second till second-to-last additional char of hostname or lowest level domain name
    rb"[A-Za-z0-9]"             #   last additional char of hostname or lowest level domain name
  rb")?"                        # }
  rb"(?:"                       # optional { (for fully qualified domain names)
    rb"\."                      #   "."
    rb"(?:"                     #   repeat {
      rb"[A-Za-z0-9]"           #     first char of intermediate level domain name
      rb"(?:"                   #     optional {
        rb"[A-Za-z0-9\-]{0,61}" #    second till second-to-last additional char of intermediate level domain name
        rb"[A-Za-z0-9]"         #       last additional char of intermediate level domain name
      rb")?"                    #     }
      rb"\."                    #     "."
    rb")*"                      #   } any number of times
    rb"[A-Za-z]{2,}"            #   top level domain name
  rb")?"                        # }
  rb"\.?"                       # a trailing dot is allowed.
);

gsbProtocolRegExp = rb"|".join([re.escape(sbProtocol) for sbProtocol in gdtxDefaultPortAndSecure_by_sbProtocol.keys()]);
gsbHostnameRegExp = rb"|".join([gsbIPv4AddressRegExp, gsbIPv6AddressRegExp, rb"\[" + gsbIPv6AddressRegExp + rb"\]", gsbDNSNameRegExp]);
# IPv6 addresses are enclosed in "[" and "]" in URLs to avoid cofusion with "host:port" separator
gsbHostnameInURLRegExp = rb"|".join([gsbIPv4AddressRegExp, rb"\[" + gsbIPv6AddressRegExp + rb"\]", gsbDNSNameRegExp]);
gsbPathRegExp     = rb"[^#?]*";
gsbQueryRegExp    = rb"[^#]*";
gsbFragmentRegExp = rb".*";

grbProtocol       = re.compile(rb"\A" + gsbProtocolRegExp + rb"\Z", re.I);
grbHostname       = re.compile(rb"\A" + gsbHostnameRegExp + rb"\Z", re.I);
grbIPv6Hostname   = re.compile(rb"\A" + gsbIPv6AddressRegExp + rb"\Z", re.I);
grbPath           = re.compile(rb"\A\/?" + gsbPathRegExp + rb"\Z", re.I);
grbQuery          = re.compile(rb"\A\??" + gsbQueryRegExp + rb"\Z", re.I);
grbFragment       = re.compile(rb"\A#?" + gsbFragmentRegExp + rb"\Z", re.I);
grbURL = re.compile(
  rb"\A"                                     # {
  rb"(" + gsbProtocolRegExp + rb")://"      #   (protocol) "://"
  rb"(" + gsbHostnameInURLRegExp + rb")"    #   (hostname)
  rb"(?:" rb"\:(\d+)" rb")?"                #   ":" (port)
  rb"(\/" + gsbPathRegExp + rb")?"          #   optional { ("/" path) }
  rb"(?:\?(" + gsbQueryRegExp + rb"))?"     #   optional { "?" (query) }
  rb"(?:\#(" + gsbFragmentRegExp + rb"))?"  #   optional { "#" (fragement) }
  rb"\Z",                                    # }
  re.I
);
grbRelativeURL = re.compile(
  rb"\A"                                     # {
  rb"(" + gsbPathRegExp + rb")?"            #   optional { (path) }
  rb"(?:\?(" + gsbQueryRegExp + rb"))?"     #   optional { "?" (query) }
  rb"(?:\#(" + gsbFragmentRegExp + rb"))?"  #   optional { "#" (fragement) }
  rb"\Z",                                    # }
  re.I
);

class cURL(object):
  sbProtocolRegExp = gsbProtocolRegExp;
  sbHostnameRegExp = gsbHostnameRegExp;
  sbPathRegExp     = gsbPathRegExp;
  sbQueryRegExp    = gsbQueryRegExp;
  sbFragmentRegExp = gsbFragmentRegExp;
  
  @classmethod
  def foFromBytesString(cClass, sbURL):
    fAssertType("sbURL", sbURL, bytes);
    oURLMatch = grbURL.match(sbURL);
    if not oURLMatch:
      raise cHTTPInvalidURLException(
        "Invalid URL",
        dxDetails = {"sbURL": sbURL},
      );
    (sbProtocol, sbHostname, sb0Port, sb0Path, sb0Query, sb0Fragment) = oURLMatch.groups();
    return cClass(
      sbProtocol, sbHostname, int(sb0Port) if sb0Port else None,
      sb0Path = sb0Path,
      sb0Query = sb0Query,
      sb0Fragment = sb0Fragment,
    );
  
  def __init__(oSelf,
    sbProtocol, sbHostname, u0PortNumber = None,
    *,
    sb0Path = None, s0URLDecodedPath = None,
    sb0Query = None, s0URLDecodedQuery = None,
    sb0Fragment = None, s0URLDecodedFragment = None,
  ):
    fAssertType("sbProtocol", sbProtocol, bytes);
    fAssertType("sbHostname", sbHostname, bytes);
    fAssertType("u0PortNumber", u0PortNumber, int, None);
    fAssertType("sb0Path", sb0Path, bytes, None);
    fAssertType("s0URLDecodedPath", s0URLDecodedPath, str, None);
    fAssertType("sb0Query", sb0Query, bytes, None);
    fAssertType("s0URLDecodedQuery", s0URLDecodedQuery, str, None);
    fAssertType("sb0Fragment", sb0Fragment, bytes, None);
    fAssertType("s0URLDecodedFragment", s0URLDecodedFragment, str, None);
    oSelf.sbProtocol = sbProtocol;
    oSelf.sbHostname = sbHostname;
    assert u0PortNumber is None or isinstance(u0PortNumber, int), \
        "u0PortNumber must be None, an int or a long, not %s" % repr(u0PortNumber);
    oSelf.__u0PortNumber = u0PortNumber;
    if s0URLDecodedPath is not None:
      assert sb0Path is None, \
          "sb0Path and s0URLDecodedPath cannot be provided together (%s and %s)" % (repr(sb0Path), repr(s0URLDecodedPath));
      oSelf.sURLDecodedPath = s0URLDecodedPath;
    else:
      oSelf.sbPath = sb0Path;
    if s0URLDecodedQuery is not None:
      assert sb0Query is None, \
          "sb0Query and s0URLDecodedQuery cannot be provided together (%s and %s)" % (repr(sb0Query), repr(s0URLDecodedQuery));
      oSelf.s0URLDecodedQuery = s0URLDecodedQuery;
    else:
      oSelf.sb0Query = sb0Query;
    if s0URLDecodedFragment is not None:
      assert sb0Fragment is None, \
          "sb0Fragment and s0URLDecodedFragment cannot be provided together (%s and %s)" % (repr(sb0Fragment), repr(s0URLDecodedFragment));
      oSelf.s0URLDecodedFragment = s0URLDecodedFragment;
    else:
      oSelf.sb0Fragment = sb0Fragment;
  
  def foFromAbsoluteOrRelativeBytesString(oSelf, sbURL):
    fAssertType("sbURL", sbURL, bytes);
    # Check if it is not an absolute URL:
    try:
      return cURL.foFromBytesString(sbURL);
    except cHTTPInvalidURLException:
      return oSelf.foFromRelativeBytesString(sbURL);
  
  def foFromRelativeBytesString(oSelf, sbURL):
    fAssertType("sbURL", sbURL, bytes);
    o0RelativeURLMatch = grbRelativeURL.match(sbURL);
    if not o0RelativeURLMatch:
      raise cHTTPInvalidURLException(
        "Invalid relative URL",
        dxDetails = {"sbURL": sbURL},
      );
    (sb0Path, sb0Query, sb0Fragment) = o0RelativeURLMatch.groups();
    if sb0Path is None:
      # If no path is provided, don't change the path in the clone.
      sbzPath = zNotProvided;
    elif sb0Path[:1] == b"/":
      # If the path starts with "/", it is absolute.
      sbzPath = sb0Path;
    else:
      # The path is relative to the folder of the current path:
      asbPath = oSelf.sbPath.rsplit(b"/")[:-1];
      bEndsWithSlash = sb0Path.endswith(b"/");
      # Apply each component of the relative path to the base path:
      for sbComponent in sb0Path.split(b"/"):
        if sbComponent == b"..":
          if len(asbPath) > 0:
            asbPath.pop();
        elif sbComponent.strip(b".") != b"":
          asbPath.append(sbComponent);
      # Make sure it ends with "/" if the relative path ended with "/":
      sbzPath = b"/".join(asbPath) + (b"/" if bEndsWithSlash else b"");
    sbzQuery = (
      # If a query is provided, it will override the existing query in the clone.
      sb0Query if sb0Query is not None else 
      # If no query is provided, but a path is, the query will be removed in the clone
      None if fbIsProvided(sbzPath) else
      # If no query or path is provided, the clone will have the same query.
      zNotProvided
    );
    sbzFragment = (
      # If a fragment is provided, it will override the existing fragment in the clone.
      sb0Fragment if sb0Fragment is not None else 
      # If no fragment is provided, but a path and/or query is, the fragment will be removed in the clone
      None if fbIsProvided(sbzPath) or fbIsProvided(sbzQuery) else
      # If no fragment, query or path is provided, the clone will have the same fragment.
      zNotProvided
    );
    return oSelf.foClone(
      sb0zPath = sbzPath,
      sb0zQuery = sbzQuery,
      sb0zFragment = sbzFragment,
    );
  
  def foClone(oSelf,
    # All these can be provided to create a modified clone of the URL. If they
    # are not provided, the value from the original is used instead.
    sbzProtocol = zNotProvided,
    sbzHostname = zNotProvided,
    u0zPortNumber = zNotProvided,
    sb0zPath = zNotProvided,
    sb0zQuery = zNotProvided,
    sb0zFragment = zNotProvided
  ):
    return cURL(
      sbProtocol   = fxGetFirstProvidedValue(sbzProtocol, oSelf.__sbProtocol),
      sbHostname   = fxGetFirstProvidedValue(sbzHostname, oSelf.__sbHostname),
      u0PortNumber = fxGetFirstProvidedValue(u0zPortNumber, oSelf.__u0PortNumber),
      sb0Path      = fxGetFirstProvidedValue(sb0zPath, oSelf.__sbPath),
      sb0Query     = fxGetFirstProvidedValue(sb0zQuery, oSelf.__sb0Query),
      sb0Fragment  = fxGetFirstProvidedValue(sb0zFragment, oSelf.__sb0Fragment),
    );
  
  ### Protocol #################################################################
  @property
  def sbProtocol(oSelf):
    return oSelf.__sbProtocol;
  @sbProtocol.setter
  def sbProtocol(oSelf, sbProtocol):
    fAssertType("sbProtocol", sbProtocol, bytes);
    assert grbProtocol.match(sbProtocol), \
        "sbProtocol is not a valid protocol (%s)" % (repr(sbProtocol),);
    oSelf.__sbProtocol = sbProtocol;
  
  @property
  def bSecure(oSelf):
    return gdtxDefaultPortAndSecure_by_sbProtocol[oSelf.__sbProtocol][1];
  
  ### Hostname #################################################################
  @property
  def sbHostname(oSelf):
    return oSelf.__sbHostname;
  @sbHostname.setter
  def sbHostname(oSelf, sbHostname):
    fAssertType("sbHostname", sbHostname, bytes);
    assert grbHostname.match(sbHostname), \
        "sbHostname is not a valid hostname (%s)" % (repr(sbHostname),);
    # IPv6 hostnames can be wrapped in "[]"; we remove these:
    oSelf.__sbHostname = sbHostname if sbHostname[0] != "[" else sbHostname[1:-1];
  
  ### Port #####################################################################
  @property
  def uPortNumber(oSelf):
    return oSelf.__u0PortNumber if oSelf.__u0PortNumber is not None else gdtxDefaultPortAndSecure_by_sbProtocol[oSelf.__sbProtocol][0];
  @property
  def u0PortNumber(oSelf):
    return oSelf.__u0PortNumber;
  @u0PortNumber.setter
  def u0PortNumber(oSelf, u0PortNumber = None):
    assert u0PortNumber is None or isinstance(u0PortNumber, int), \
        "u0PortNumber must be None, an int or a long, not %s" % repr(u0PortNumber);
    oSelf.__u0PortNumber = u0PortNumber;
  
  ### Path #####################################################################
  # path getter and setter
  @property
  def sbPath(oSelf):
    return oSelf.__sbPath;
  @sbPath.setter
  def sbPath(oSelf, sb0Path):
    fAssertType("sb0Path", sb0Path, bytes, None);
    if sb0Path is None:
      oSelf.__sbPath = b"/";
    else:
      assert grbPath.match(sb0Path), \
          "sb0Path is not a valid path (%s)" % (repr(sb0Path),);
      # Automatically add "/" prefix if missing.
      oSelf.__sbPath = (b"/" if (sb0Path[:1] != b"/") else b"") + sb0Path;
  
  # URL decoded path getter and setter
  @property
  def sURLDecodedPath(oSelf):
    return urllib.parse.unquote(oSelf.__sbPath);
  @sURLDecodedPath.setter
  def sURLDecodedPath(oSelf, sURLDecodedPath):
    oSelf.sbPath = bytes(urllib.parse.quote(sURLDecodedPath), "ascii", "strict");
  
  # URL decoded path array getter
  @property
  def asURLDecodedPath(oSelf):
    # "/A/B//C%2F%44/" => ["A", "B", "C", "D"]
    return [s for s in oSelf.sURLDecodedPath.split("/") if s] if oSelf.__sbPath != b"/" else [];
  
  ### Query ####################################################################
  # query getter and setter
  @property
  def sb0Query(oSelf):
    return oSelf.__sb0Query;
  @sb0Query.setter
  def sb0Query(oSelf, sb0Query):
    fAssertType("sb0Query", sb0Query, bytes, None);
    if sb0Query is not None:
      assert grbQuery.match(sb0Query), \
          "sb0Query is not a valid query (%s)" % (repr(sb0Query),);
    oSelf.__sb0Query = sb0Query;
  
  # URL decoded query getter and setter
  @property
  def s0URLDecodedQuery(oSelf):
    return urllib.parse.unquote(oSelf.__sb0Query) if oSelf.__sb0Query is not None else None;
  @s0URLDecodedQuery.setter
  def s0URLDecodedQuery(oSelf, s0URLDecodedQuery):
    fAssertType("s0URLDecodedQuery", s0URLDecodedQuery, str, None);
    if s0URLDecodedQuery is not None:
      sbQuery = bytes(urllib.parse.quote(s0URLDecodedQuery), "ascii", "strict");
      assert grbQuery.match(sbQuery), \
          "s0URLDecodedQuery (%s) does not encode to a valid query (%s)" % (repr(s0URLDecodedQuery), repr(sbQuery));
      oSelf.__sb0Query = sbQuery;
    else:
      oSelf.__sb0Query = None;
  
  # query dictionary get and set
  def fdsGetQueryDict(oSelf):
    return fdsURLDecodedNameValuePairsFromBytesString(oSelf.__sb0Query) if oSelf.__sb0Query else {};
  def fSetQueryDict(oSelf, d0sQueryValue_by_sName):
    assert d0sQueryValue_by_sName is None or isinstance(d0sQueryValue_by_sName, dict), \
        "d0sQueryValue_by_sbName must be 'None' or 'dict', not %s (%s)" % \
        (type(d0sQueryValue_by_sName), repr(d0sQueryValue_by_sName));
    oSelf.__sb0Query = fsbURLEncodedNameValuePairsToBytesString(d0sQueryValue_by_sName) \
        if d0sQueryValue_by_sName is not None else None;
  
  # query values get and set
  def fs0GetQueryValue(oSelf, sName):
    dsQueryValue_by_sName = oSelf.fdsGetQueryDict();
    return dsQueryValue_by_sName.get(sName);
  def fSetQueryValue(oSelf, sName, sValue):
    dsQueryValue_by_sName = oSelf.fdsGetQueryDict();
    dsQueryValue_by_sName[sName] = sValue;
    oSelf.fSetQueryDict(dsQueryValue_by_sName);
  
  ### Fragment #################################################################
  # fragment getter and setter
  @property
  def sb0Fragment(oSelf):
    return oSelf.__sb0Fragment;
  @sb0Fragment.setter
  def sb0Fragment(oSelf, sb0Fragment):
    fAssertType("sb0Fragment", sb0Fragment, bytes, None);
    if sb0Fragment is not None:
      assert grbFragment.match(sb0Fragment), \
          "sb0Fragment is not a valid fragment (%s)" % (repr(sb0Fragment),);
    oSelf.__sb0Fragment = sb0Fragment;
  # URL decoded fragment getter and setter
  @property
  def sURLDecodedFragment(oSelf):
    return urllib.parse.unquote(oSelf.__sb0Fragment) if oSelf.__sb0Fragment is not None else None;
  @sURLDecodedFragment.setter
  def sURLDecodedFragment(oSelf, sURLDecodedFragment):
    oSelf.__sb0Fragment = bytes(urllib.parse.quote(sURLDecodedFragment), "ascii", "strict");
  
  ### Convenience ##############################################################
  @property
  def sbAddress(oSelf):
    return (b"[%s]:%d" if grbIPv6Hostname.match(oSelf.__sbHostname) else b"%s:%d") % \
        (oSelf.__sbHostname, oSelf.uPortNumber);
  
  @property
  def sbHostnameAndOptionalPort(oSelf):
    bNonDefaultPortNumber = oSelf.__u0PortNumber not in [None, gdtxDefaultPortAndSecure_by_sbProtocol[oSelf.__sbProtocol][0]];
    return (
      b"[%s]" % oSelf.__sbHostname if grbIPv6Hostname.match(oSelf.__sbHostname) else oSelf.__sbHostname
    ) + (
      b":%d" % oSelf.__u0PortNumber if bNonDefaultPortNumber else b""
    );
  
  @property
  def oBase(oSelf):
    return cURL(sbProtocol = oSelf.__sbProtocol, sbHostname = oSelf.__sbHostname, u0PortNumber = oSelf.__u0PortNumber);
  
  @property
  def sbBase(oSelf):
    return b"%s://%s" % (oSelf.__sbProtocol, oSelf.sbHostnameAndOptionalPort);
  @property
  def sbOrigin(oSelf):
    return b"%s://%s" % (oSelf.__sbProtocol, oSelf.sbAddress);
  
  @property
  def sbRelative(oSelf):
    return b"".join([
      oSelf.__sbPath,
      (b"?" + oSelf.__sb0Query) if oSelf.__sb0Query is not None else b"",
      (b"#" + oSelf.__sb0Fragment) if oSelf.__sb0Fragment is not None else b"",
    ]);
  @property
  def sbAbsolute(oSelf):
    return oSelf.sbBase + oSelf.sbRelative;
  
  def __str__(oSelf):
    return str(oSelf.sbAbsolute, 'ascii', 'strict');
  
  def fasDump(oSelf):
    return [
      "sbProtocol: %s" % repr(oSelf.__sbProtocol),
      "sbHostname: %s" % repr(oSelf.__sbHostname),
      "u0PortNumber: %s" % repr(oSelf.__u0PortNumber),
      "sbPath: %s" % repr(oSelf.__sbPath),
      "sb0Query: %s" % repr(oSelf.__sb0Query),
      "sb0Fragment: %s" % repr(oSelf.__sb0Fragment),
    ];
  
  def fsToString(oSelf):
    return "%s{%s}" % (oSelf.__class__.__name__, str(oSelf.sbAbsolute, 'ascii', 'strict'));
  
  def __repr__(oSelf):
    return "<%s.%s %s://%s%s%s%s%s>" % (
      oSelf.__class__.__module__,
      oSelf.__class__.__name__,
      repr(oSelf.__sbProtocol),
      repr(oSelf.__sbHostname),
      (":%s" % repr(oSelf.__u0PortNumber)) if oSelf.__u0PortNumber is not None else "",
      repr(oSelf.__sbPath),
      ("?%s" % repr(oSelf.__sb0Query)) if oSelf.__sb0Query is not None else "",
      ("#%s" % repr(oSelf.__sb0Fragment)) if oSelf.__sb0Fragment is not None else "",
    );
  
for cException in acExceptions:
  setattr(cURL, cException.__name__, cException);
