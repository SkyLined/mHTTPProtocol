import re, urllib.parse;

from mNotProvided import fAssertType, fbIsProvided, fxGetFirstProvidedValue, zNotProvided;

from .fdsURLDecodedNameValuePairsFromBytesString import fdsURLDecodedNameValuePairsFromBytesString;
from .fsbURLEncodedNameValuePairsToBytesString import fsbURLEncodedNameValuePairsToBytesString;
from .mExceptions import cHTTPInvalidURLException, acExceptions;

gdtxDefaultPortNumberAndSecure_by_sbProtocol = {
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
grbIPv4Byte = re.compile(gsbIPv4ByteRegExp); # sanity check
gsbIPv4AddressRegExp   = rb"(?:" + gsbIPv4ByteRegExp + rb"\." rb"){3}" + gsbIPv4ByteRegExp; # 0.1.2.3
grbIPv4Address = re.compile(gsbIPv4AddressRegExp); # sanity check

gsbIPv6WordRegExp      = rb"[0-9a-fA-F]{1,4}";
grbIPv6Word = re.compile(gsbIPv6WordRegExp); # sanity check
gsbIPv6PreWordRegExp   = rb"(?:" + gsbIPv6WordRegExp + rb"\:" rb")";
grbIPv6PreWord = re.compile(gsbIPv6PreWordRegExp); # sanity check
gsbIPv6PostWordRegExp   = rb"(?:" rb"\:" + gsbIPv6WordRegExp + rb")";
grbIPv6PostWord = re.compile(gsbIPv6PostWordRegExp); # sanity check
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
grbIPv6Address = re.compile(gsbIPv6AddressRegExp); # sanity check

gsbDNSNameRegExp = (
  rb"(?:"                               # treat as a single entity {
    rb"[A-Za-z0-9]"                     #   first char of hostname or lowest level domain name
    rb"(?:"                             #   optional {
      rb"[A-Za-z0-9\-]{0,61}"           #     second till second-to-last additional char of hostname or lowest level domain name
      rb"[A-Za-z0-9]"                   #     last additional char of hostname or lowest level domain name
    rb")?"                              #   }
    rb"(?:"                             #   optional { (for fully qualified domain names)
      rb"\."                            #     "."
      rb"(?:"                           #     repeat {
        rb"[A-Za-z0-9]"                 #       first char of intermediate level domain name
        rb"(?:"                         #       optional {
          rb"[A-Za-z0-9\-]{0,61}"       #      second till second-to-last additional char of intermediate level domain name
          rb"[A-Za-z0-9]"               #         last additional char of intermediate level domain name
        rb")?"                          #       }
        rb"\."                          #       "."
      rb")*"                            #     } any number of times
      rb"[A-Za-z]{2,}"                  #     top level domain name
    rb")?"                              #   }
    rb"\.?"                             #   a trailing dot is allowed.
  rb")"                                 # }
);
grbDNSName = re.compile(gsbDNSNameRegExp); # sanity check

gsbProtocolRegExp = (
  rb"(?:" + rb"|".join([              #   any one of the known protocols
    re.escape(sbProtocol)             #
    for sbProtocol in gdtxDefaultPortNumberAndSecure_by_sbProtocol.keys()
  ]) + rb")"                          #
);
grbProtocol = re.compile(gsbProtocolRegExp); # sanity check

gsbUsernameRegExp = (
  rb"(?:"                             #   repeat {
    rb"[\w\-\.~!\$&'\(\)\*\+,;=]"     #     characters that do not need encoding
  rb"|"                               #   } or {
    rb"%[0-9A-F]{2}"                  #     percent-encoded character
  rb")+"                              #   } at least once
);
grbUsername = re.compile(gsbUsernameRegExp); # sanity check

# rfc3986 deprecates passwords but we offer backwards compatibility
gsbPasswordRegExp = (
  rb"(?:"                               # treat as a single entity {
    rb"\b"                              #   cannot be preceded by certain chars.
    rb"(?:"                             #   repeat {
      rb"[\w\-\.~!\$&'\(\)\*\+,;=]"     #     characters that do not need encoding
    rb"|"                               #   } or {
      rb"%[0-9A-F]{2}"                  #     percent-encoded character
    rb")*"                              #   } any number of times
    rb"\b"                              #   cannot be followed by certain chars.
  rb")"                                 # }
);
grbPassword = re.compile(gsbPasswordRegExp); # sanity check

gsbHostRegExp = (                       # IPv6 can optionally be wrapped in square brackets.
  rb"(?:" + rb"|".join([              #   one of the following {
    gsbIPv4AddressRegExp,             #     <IPv4>
    gsbIPv6AddressRegExp,             #     <IPv6>
    rb"\[" + gsbIPv6AddressRegExp + rb"\]", # "[" <IPv6> "]"
    gsbDNSNameRegExp,                 #     <DNS name>
  ]) + rb")"                          #   }
);
grbHost = re.compile(gsbHostRegExp); # sanity check

gsbHostInURLRegExp = (                  # URLs only allow IPv6 in square brackets to avoid confusion with ":<port number>".
  rb"(?:"                               # treat as a single entity {
    rb"(?:" + rb"|".join([              #   one of the following {
      gsbIPv4AddressRegExp,             #     <IPv4>
      rb"\[" + gsbIPv6AddressRegExp + rb"\]", # "[" <IPv6> "]"
      gsbDNSNameRegExp,                 #     <DNS name>
    ]) + rb")"                          #   }
  rb")"                                 # }
);
grbHostInURL = re.compile(gsbHostInURLRegExp); # sanity check

gsbPortNumberRegExp = (
  rb"(?:"                               # treat as a single entity {
    rb"\b"                              #   cannot be preceded by certain chars.
    rb"0*"                              #   any number of preceding zeros
    rb"(?:" + rb"|".join([              #   one of the following {
      rb"\d{1,4}",                      #         0- 9999
      rb"[1-5]\d{4}",                   #     10000-59999
      rb"6[0-4]\d{3}",                  #     60000-64999
      rb"65[0-4]\d{2}",                 #     65000-65499
      rb"655[0-2]\d",                   #     65500-65520
      rb"6553[0-5]",                    #     65530-65535
    ]) + rb")"                          #   }
    rb"\b"                              #   cannot be followed by certain chars.
  rb")"                                 # }
);
grbPortNumber = re.compile(gsbPortNumberRegExp); # sanity check

gsbPathRegExp     = rb"[A-Za-z0-9~!@$%&*()_+\-=[\];'/:|,./]*";
gsbQueryRegExp    = rb"[A-Za-z0-9`~!@$%^&*()_+\-={}[\]:|;\\,./?]*";
gsbFragmentRegExp = rb".*";

grbProtocol       = re.compile(rb"\A" + gsbProtocolRegExp + rb"\Z");
grbUsername       = re.compile(rb"\A" + gsbUsernameRegExp + rb"\Z");
grbPassword       = re.compile(rb"\A" + gsbPasswordRegExp + rb"\Z");
grbHost           = re.compile(rb"\A" + gsbHostRegExp + rb"\Z");
grbIPv6Address    = re.compile(rb"\A" + gsbIPv6AddressRegExp + rb"\Z");
grbPath           = re.compile(rb"\A\/?" + gsbPathRegExp + rb"\Z");
grbQuery          = re.compile(rb"\A\??" + gsbQueryRegExp + rb"\Z");
grbFragment       = re.compile(rb"\A#?" + gsbFragmentRegExp + rb"\Z");

grbURL = re.compile(
  rb"\A"                                    # start of string
  rb"(" + gsbProtocolRegExp + rb")://"      # (protocol) "://"
  rb"(?:"                                   # optional {
    rb"(" + gsbUsernameRegExp + rb")"       #   (username)
    rb"(?:"                                 #   optional {
      rb"\:(" + gsbPasswordRegExp + rb")"   #    ":" (password)
    rb")?"                                  #   }
    rb"@"                                   #   "@"
  rb")?"                                    # }
  rb"(" + gsbHostInURLRegExp + rb")"        # (host)
  rb"(?:"                                   # optional {
    rb"\:(" + gsbPortNumberRegExp + rb")"   #   ":" (port number)
  rb")?"                                    # }
  rb"(\/" + gsbPathRegExp + rb")?"          # optional { ("/" path) }
  rb"(?:\?(" + gsbQueryRegExp + rb"))?"     # optional { "?" (query) }
  rb"(?:\#(" + gsbFragmentRegExp + rb"))?"  # optional { "#" (fragment) }
  rb"\Z"                                    # end of string
);
grbRelativeURL = re.compile(
  rb"\A"                                    # start of string
  rb"(" + gsbPathRegExp + rb")?"            #   optional { (path) }
  rb"(?:\?(" + gsbQueryRegExp + rb"))?"     #   optional { "?" (query) }
  rb"(?:\#(" + gsbFragmentRegExp + rb"))?"  #   optional { "#" (fragment) }
  rb"\Z"                                    # end of string
);

class cURL(object):
  sbProtocolRegExp    = gsbProtocolRegExp;
  sbUsernameRegExp    = gsbUsernameRegExp;
  sbPasswordRegExp    = gsbPasswordRegExp;
  sbHostRegExp        = gsbHostRegExp;
  sbPortNumberRegExp  = gsbPortNumberRegExp;
  sbPathRegExp        = gsbPathRegExp;
  sbQueryRegExp       = gsbQueryRegExp;
  sbFragmentRegExp    = gsbFragmentRegExp;
  
  @classmethod
  def foFromBytesString(cClass, sbURL):
    fAssertType("sbURL", sbURL, bytes);
    oURLMatch = grbURL.match(sbURL);
    if not oURLMatch:
      raise cHTTPInvalidURLException(
        "Invalid URL",
        dxDetails = {"sbURL": sbURL},
      );
    (
      sbProtocol,
      sb0Username,
      sb0Password,
      sbHost,
      sb0PortNumber,
      sb0Path,
      sb0Query,
      sb0Fragment,
    ) = oURLMatch.groups();
    return cClass(
      sbProtocol = sbProtocol,
      sb0Username = sb0Username,
      sb0Password = sb0Password,
      sbHost = sbHost,
      u0PortNumber = int(sb0PortNumber) if sb0PortNumber else None,
      sb0Path = sb0Path,
      sb0Query = sb0Query,
      sb0Fragment = sb0Fragment,
    );
  
  def __init__(oSelf,
    sbProtocol,
    sbHost,
    u0PortNumber = None,
    *,
    sb0Username = None, s0URLDecodedUsername = None,
    sb0Password = None, s0URLDecodedPassword = None,
    sb0Path = None, s0URLDecodedPath = None,
    sb0Query = None, s0URLDecodedQuery = None,
    sb0Fragment = None, s0URLDecodedFragment = None,
  ):
    fAssertType("sbProtocol", sbProtocol, bytes);
    fAssertType("sb0Username", sb0Username, bytes, None);
    fAssertType("s0URLDecodedUsername", s0URLDecodedUsername, str, None);
    fAssertType("sb0Password", sb0Password, bytes, None);
    fAssertType("s0URLDecodedPassword", s0URLDecodedPassword, str, None);
    fAssertType("sbHost", sbHost, bytes);
    fAssertType("u0PortNumber", u0PortNumber, int, None);
    fAssertType("sb0Path", sb0Path, bytes, None);
    fAssertType("s0URLDecodedPath", s0URLDecodedPath, str, None);
    fAssertType("sb0Query", sb0Query, bytes, None);
    fAssertType("s0URLDecodedQuery", s0URLDecodedQuery, str, None);
    fAssertType("sb0Fragment", sb0Fragment, bytes, None);
    fAssertType("s0URLDecodedFragment", s0URLDecodedFragment, str, None);
    oSelf.sbProtocol = sbProtocol;
    
    if s0URLDecodedUsername is not None:
      assert sb0Username is None, \
          "sb0Path and s0URLDecodedUsername cannot be provided together (%s and %s)" % (repr(sb0Path), repr(s0URLDecodedUsername));
      oSelf.s0URLDecodedUsername = s0URLDecodedUsername;
    else:
      oSelf.sb0Username = sb0Username;
    
    if s0URLDecodedPassword is not None:
      assert sb0Password is None, \
          "sb0Path and s0URLDecodedPassword cannot be provided together (%s and %s)" % (repr(sb0Path), repr(s0URLDecodedPassword));
      oSelf.s0URLDecodedPassword = s0URLDecodedPassword;
    else:
      oSelf.sb0Password = sb0Password;
    
    oSelf.sbHost = sbHost;
    
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
    sb0zUsername = zNotProvided,
    sb0zPassword = zNotProvided,
    sbzHost = zNotProvided,
    u0zPortNumber = zNotProvided,
    sb0zPath = zNotProvided,
    sb0zQuery = zNotProvided,
    sb0zFragment = zNotProvided
  ):
    return cURL(
      sbProtocol   = fxGetFirstProvidedValue(sbzProtocol, oSelf.sbProtocol),
      sb0Username  = fxGetFirstProvidedValue(sb0zUsername, oSelf.sb0Username),
      sb0Password  = fxGetFirstProvidedValue(sb0zPassword, oSelf.sb0Password),
      sbHost       = fxGetFirstProvidedValue(sbzHost, oSelf.sbHost),
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
    return gdtxDefaultPortNumberAndSecure_by_sbProtocol[oSelf.__sbProtocol][1];
  
  ### Username #################################################################
  # username getter and setter
  @property
  def sb0Username(oSelf):
    return oSelf.__sb0Username;
  @sb0Username.setter
  def sb0Username(oSelf, sb0Username):
    fAssertType("sb0Username", sb0Username, bytes, None);
    if sb0Username is not None:
      assert grbUsername.match(sb0Username), \
          "sb0Username is not a valid Username (%s)" % (repr(sb0Username),);
    oSelf.__sb0Username = sb0Username;
  # URL decoded username getter and setter
  @property
  def sURLDecodedUsername(oSelf):
    return urllib.parse.unquote(oSelf.__sb0Username) if oSelf.__sb0Username is not None else None;
  @sURLDecodedUsername.setter
  def sURLDecodedUsername(oSelf, sURLDecodedUsername):
    oSelf.__sb0Username = bytes(urllib.parse.quote(sURLDecodedUsername), "ascii", "strict");
  
  ### Password #################################################################
  # password getter and setter
  @property
  def sb0Password(oSelf):
    return oSelf.__sb0Password;
  @sb0Password.setter
  def sb0Password(oSelf, sb0Password):
    fAssertType("sb0Password", sb0Password, bytes, None);
    if sb0Password is not None:
      assert grbPassword.match(sb0Password), \
          "sb0Password is not a valid Password (%s)" % (repr(sb0Password),);
    oSelf.__sb0Password = sb0Password;
  # URL decoded password getter and setter
  @property
  def sURLDecodedPassword(oSelf):
    return urllib.parse.unquote(oSelf.__sb0Password) if oSelf.__sb0Password is not None else None;
  @sURLDecodedPassword.setter
  def sURLDecodedPassword(oSelf, sURLDecodedPassword):
    oSelf.__sb0Password = bytes(urllib.parse.quote(sURLDecodedPassword), "ascii", "strict");
  
  ### Host #####################################################################
  @property
  def sbHost(oSelf):
    return oSelf.__sbHost;
  @sbHost.setter
  def sbHost(oSelf, sbHost):
    fAssertType("sbHost", sbHost, bytes);
    assert grbHost.match(sbHost), \
        "sbHost is not valid (%s)" % (repr(sbHost),);
    # IPv6 addresses can optionally be wrapped in "[]"; we remove these:
    oSelf.__sbHost = sbHost if sbHost[0] != "[" else sbHost[1:-1];
  
  ### Port #####################################################################
  @property
  def uPortNumber(oSelf):
    return oSelf.__u0PortNumber if oSelf.__u0PortNumber is not None else gdtxDefaultPortNumberAndSecure_by_sbProtocol[oSelf.__sbProtocol][0];
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
    if grbIPv6Address.match(oSelf.__sbHost):
      return b"[%s]:%d" % (oSelf.__sbHost, oSelf.uPortNumber);
    return b"%s:%d" % (oSelf.__sbHost, oSelf.uPortNumber);

  @property
  def sbHostAndOptionalPort(oSelf):
    sbHostAndOptionalPort = b"";
    if grbIPv6Address.match(oSelf.__sbHost):
      sbHostAndOptionalPort += b"[%s]" % oSelf.__sbHost;
    else:
      sbHostAndOptionalPort += oSelf.__sbHost;
    
    if oSelf.__u0PortNumber not in [None, gdtxDefaultPortNumberAndSecure_by_sbProtocol[oSelf.__sbProtocol][0]]:
      sbHostAndOptionalPort += b":%d" % oSelf.__u0PortNumber;
    return sbHostAndOptionalPort;

  @property
  def sbAuthority(oSelf):
    if oSelf.__sb0Username is None and oSelf.__sb0Password is None:
      sbUserInfo = b""; # some components are optional, we'll add them as needed:
    else:
      sbUserInfo = oSelf.__sb0Username or b"";
      if oSelf.__sb0Password is not None:
        sbUserInfo += b":" + oSelf.__sb0Password;
      sbUserInfo += b"@";
    return sbUserInfo + oSelf.sbHostAndOptionalPort;
  
  @property
  def oBase(oSelf):
    return cURL(sbProtocol = oSelf.__sbProtocol, sbHost = oSelf.__sbHost, u0PortNumber = oSelf.__u0PortNumber);
  
  @property
  def sbBase(oSelf):
    return b"%s://%s" % (oSelf.__sbProtocol, oSelf.sbHostAndOptionalPort);
  
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
      "sb0Username: %s" % repr(oSelf.__sb0Username),
      "sb0Password: %s" % repr(oSelf.__sb0Password),
      "sbHost: %s" % repr(oSelf.__sbHost),
      "u0PortNumber: %s" % repr(oSelf.__u0PortNumber),
      "sbPath: %s" % repr(oSelf.__sbPath),
      "sb0Query: %s" % repr(oSelf.__sb0Query),
      "sb0Fragment: %s" % repr(oSelf.__sb0Fragment),
    ];
  
  def fsToString(oSelf):
    return "%s{%s}" % (oSelf.__class__.__name__, str(oSelf.sbAbsolute, 'ascii', 'strict'));
  
  def __repr__(oSelf):
    return "".join([
      "<",
      oSelf.__class__.__module__,
      ".",
      oSelf.__class__.__name__,
      " ",
      repr(oSelf.__sbProtocol),
      "://",
      ("%s%s@" % (
        repr(oSelf.__sb0Username) if oSelf.__sb0Username is not None else "",
        (":%s" % repr(oSelf.__sb0Password)) if oSelf.__sb0Password is not None else "",
      )) if oSelf.__sb0Username is not None or oSelf.__sb0Password is not None else "",
      repr(oSelf.__sbHost),
      (":%s" % repr(oSelf.__u0PortNumber)) if oSelf.__u0PortNumber is not None else "",
      repr(oSelf.__sbPath),
      ("?%s" % repr(oSelf.__sb0Query)) if oSelf.__sb0Query is not None else "",
      ("#%s" % repr(oSelf.__sb0Fragment)) if oSelf.__sb0Fragment is not None else "",
    ]);
  
for cException in acExceptions:
  setattr(cURL, cException.__name__, cException);
