import re;

from mNotProvided import fbIsProvided, fxGetFirstProvidedValue, zNotProvided;

from ..mExceptions import cInvalidURLException;

from .fdxURLDecodedNameValuePairs import fdxURLDecodedNameValuePairs;
from .fsbURLEncodedNameValuePairs import fsbURLEncodedNameValuePairs;
from .fsbURLEncode import fsbURLEncode;
from .fsURLDecode import fsURLDecode;
# more imports at end of file to avoid circular imports

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
# Now create a second reg.exp. that allows anything that looks remotely like a
# URL. String that match this are not technically valid URLs but they may be
# close enough to be used and pass checks while triggering issues in the code
# handling them.
gsbInvalidUsernameRegExp    = rb"[^:@]*";   # Anything that's not start of password or host
gsbInvalidPasswordRegExp    = rb"[^@]*";    # Anything that's not start of host
gsbInvalidHostInURLRegExp   = rb"[^:/\?#]*";# Anything that's not start of port, path, query or fragment
gsbInvalidPortNumberRegExp  = rb"[^/\?#]*"; # Anything that's not start of path, query or fragment
gsbInvalidPathRegExp        = rb"[^\?#]*";  # Anything that's not start of query or fragment
gsbInvalidQueryRegExp       = rb"[^#]*";    # Anything that's not start of fragment
# There is not "invalid fragment" reg.exp. since the original is already allows
# any bytes.
grbInvalidURL = re.compile(
  rb"\A"                                    # start of string
  rb"(" + gsbProtocolRegExp + rb")://"      # (protocol) "://"
  rb"(?:"                                   # optional {
    rb"(" + gsbInvalidUsernameRegExp + rb")"#   (username)
    rb"(?:"                                 #   optional {
      rb"\:(" + gsbInvalidPasswordRegExp + rb")" # ":" (password)
    rb")?"                                  #   }
    rb"@"                                   #   "@"
  rb")?"                                    # }
  rb"(" + gsbInvalidHostInURLRegExp + rb")" # (host)
  rb"(?:"                                   # optional {
    rb"\:(" + gsbInvalidPortNumberRegExp + rb")"# ":" (port number)
  rb")?"                                    # }
  rb"(\/" + gsbInvalidPathRegExp + rb")?"   # optional { ("/" path) }
  rb"(?:\?(" + gsbInvalidQueryRegExp + rb"))?" # optional { "?" (query) }
  rb"(?:\#(" + gsbFragmentRegExp + rb"))?"  # optional { "#" (fragment) }
  rb"\Z"                                    # end of string
);
grbInvalidRelativeURL = re.compile(
  rb"\A"                                    # start of string
  rb"(" + gsbInvalidPathRegExp + rb")?"            #   optional { (path) }
  rb"(?:\?(" + gsbInvalidQueryRegExp + rb"))?"     #   optional { "?" (query) }
  rb"(?:\#(" + gsbFragmentRegExp + rb"))?"  #   optional { "#" (fragment) }
  rb"\Z"                                    # end of string
);
grbInvalidPath   = re.compile(rb"\A\/?" + gsbInvalidPathRegExp + rb"\Z");
grbInvalidQuery  = re.compile(rb"\A\??" + gsbInvalidQueryRegExp + rb"\Z");
  

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
  def foFromBytesString(cClass,
    sbURL: bytes,
    bAllowInvalidURLs: bool = False,
  ) -> "cURL":
    o0URLMatch = (grbInvalidURL if bAllowInvalidURLs else grbURL).match(sbURL); # grbURL.match(sbURL)
    if o0URLMatch is None:
      raise cInvalidURLException(
        "Cannot parse URL",
        sbData = sbURL,
      );
      # The URL is not technically valid but it is parsable.
    (
      sbProtocol,
      sb0Username,
      sb0Password,
      sbHost,
      sb0PortNumber,
      sb0Path,
      sb0Query,
      sb0Fragment,
    ) = o0URLMatch.groups();
    return cClass(
      sbProtocol = sbProtocol,
      sb0Username = sb0Username,
      sb0Password = sb0Password,
      sbHost = sbHost,
      u0PortNumber = int(sb0PortNumber) if sb0PortNumber else None,
      sb0Path = sb0Path,
      sb0Query = sb0Query,
      sb0Fragment = sb0Fragment,
      bAllowInvalidURLs = bAllowInvalidURLs,
    );
  
  def __init__(oSelf,
    sbProtocol: bytes,
    sbHost : bytes,
    u0PortNumber: int | None = None,
    *,
    sb0Username: bytes |  None = None,
    s0Username: str |  None = None, # will be URL encoded
    sb0Password: bytes |  None = None,
    s0Password: str |  None = None, # will be URL encoded
    sb0Path: bytes |  None = None,
    s0Path: str |  None = None, # will be URL encoded
    sb0Query: bytes |  None = None,
    s0Query: str |  None = None, # will be URL encoded
    sb0Fragment: bytes |  None = None,
    s0Fragment: str |  None = None, # will be URL encoded
    bAllowInvalidURLs: bool = False,
  ):
    # We have to set this first because the setters for some of the properties
    # need to check the value:
    oSelf.bAllowInvalidURLs = bAllowInvalidURLs;
    
    oSelf.sbProtocol = sbProtocol;
    
    if s0Username is not None:
      assert sb0Username is None, \
          "sb0Username and s0Username cannot be provided together (%s and %s)" % (repr(sb0Path), repr(s0Username));
      oSelf.s0Username = s0Username;
    else:
      oSelf.sb0Username = sb0Username;
    
    if s0Password is not None:
      assert sb0Password is None, \
          "sb0Password and s0Password cannot be provided together (%s and %s)" % (repr(sb0Path), repr(s0Password));
      oSelf.s0Password = s0Password;
    else:
      oSelf.sb0Password = sb0Password;
    
    oSelf.sbHost = sbHost;
    
    oSelf.__u0PortNumber = u0PortNumber;
    
    if s0Path is not None:
      assert sb0Path is None, \
          "sb0Path and s0Path cannot be provided together (%s and %s)" % (repr(sb0Path), repr(s0Path));
      oSelf.sPath = s0Path;
    else:
      oSelf.sbPath = sb0Path or b"";
    
    if s0Query is not None:
      assert sb0Query is None, \
          "sb0Query and s0Query cannot be provided together (%s and %s)" % (repr(sb0Query), repr(s0Query));
      oSelf.s0Query = s0Query;
    else:
      oSelf.sb0Query = sb0Query;
    
    if s0Fragment is not None:
      assert sb0Fragment is None, \
          "sb0Fragment and s0Fragment cannot be provided together (%s and %s)" % (repr(sb0Fragment), repr(s0Fragment));
      oSelf.s0Fragment = s0Fragment;
    else:
      oSelf.sb0Fragment = sb0Fragment;

  def foFromAbsoluteOrRelativeBytesString(oSelf,
    sbURL: bytes,
    bAllowInvalidURLs: bool = None,
  ) -> "cURL":
    # If not provided, that value of the base URL is used:
    if bAllowInvalidURLs is None:
      bAllowInvalidURLs = oSelf.bAllowInvalidURLs;
    # Check if it is not an absolute URL:
    try:
      return cURL.foFromBytesString(sbURL, bAllowInvalidURLs);
    except cInvalidURLException:
      return oSelf.foFromRelativeBytesString(sbURL, bAllowInvalidURLs);
  
  def foFromRelativeBytesString(oSelf,
    sbURL: bytes,
    bAllowInvalidURLs: bool = None,
  ) -> "cURL":
    # If not provided, that value of the base URL is used:
    if bAllowInvalidURLs is None:
      bAllowInvalidURLs = oSelf.bAllowInvalidURLs;
    o0RelativeURLMatch = (grbInvalidRelativeURL if bAllowInvalidURLs else grbRelativeURL).match(sbURL); # grbRelativeURL.match(sbURL);
    if not o0RelativeURLMatch:
      raise cInvalidURLException(
        "Invalid relative URL",
        sbData = sbURL,
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
    sbzProtocol: bytes | type(zNotProvided) = zNotProvided,
    sb0zUsername: bytes | type(zNotProvided) = zNotProvided,
    sb0zPassword : bytes | type(zNotProvided)= zNotProvided,
    sbzHost: bytes | type(zNotProvided) = zNotProvided,
    u0zPortNumber: bytes | type(zNotProvided) = zNotProvided,
    sb0zPath: bytes | type(zNotProvided) = zNotProvided,
    sb0zQuery: bytes | type(zNotProvided) = zNotProvided,
    sb0zFragment: bytes | type(zNotProvided) = zNotProvided
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
  def sbProtocol(oSelf) -> bytes:
    return oSelf.__sbProtocol;
  @sbProtocol.setter
  def sbProtocol(oSelf,
    sbProtocol: bytes,
  ):
    assert grbProtocol.match(sbProtocol), \
        "sbProtocol is not a valid protocol (%s)" % (repr(sbProtocol),);
    oSelf.__sbProtocol = sbProtocol;
  
  @property
  def bSecure(oSelf) -> bool:
    return gdtxDefaultPortNumberAndSecure_by_sbProtocol[oSelf.__sbProtocol][1];
  
  ### Username #################################################################
  # username getter and setter
  @property
  def sb0Username(oSelf) -> bytes:
    return oSelf.__sb0Username;
  @sb0Username.setter
  def sb0Username(oSelf,
    sb0Username: bytes | None,
  ):
    if sb0Username is not None:
      assert grbUsername.match(sb0Username), \
          "sb0Username is not a valid Username (%s)" % (repr(sb0Username),);
    oSelf.__sb0Username = sb0Username;
  # URL decoded username getter and setter
  @property
  def s0Username(oSelf) -> str | None:
    return fsURLDecode(oSelf.__sb0Username) if oSelf.__sb0Username is not None else None;
  @s0Username.setter
  def s0Username(oSelf,
    s0Username: str | None,
  ):
    oSelf.__sb0Username = fsbURLEncode(sUsername);
  
  ### Password #################################################################
  # password getter and setter
  @property
  def sb0Password(oSelf) -> bytes:
    return oSelf.__sb0Password;
  @sb0Password.setter
  def sb0Password(oSelf,
    sb0Password: bytes | None,
  ):
    if sb0Password is not None:
      assert grbPassword.match(sb0Password), \
          "sb0Password is not a valid Password (%s)" % (repr(sb0Password),);
    oSelf.__sb0Password = sb0Password;
  # URL decoded password getter and setter
  @property
  def s0Password(oSelf) -> str | None:
    return fsURLDecode(oSelf.__sb0Password) if oSelf.__sb0Password is not None else None;
  @s0Password.setter
  def s0Password(oSelf,
    s0Password: str | None,
  ):
    oSelf.__sb0Password = fsbURLEncode(sPassword);
  
  ### Host #####################################################################
  @property
  def sbHost(oSelf) -> bytes:
    return oSelf.__sbHost;
  @sbHost.setter
  def sbHost(oSelf,
    sbHost: bytes,
  ):
    assert grbHost.match(sbHost), \
        "sbHost is not valid (%s)" % (repr(sbHost),);
    # IPv6 addresses can optionally be wrapped in "[]"; we remove these:
    oSelf.__sbHost = sbHost if sbHost[0] != "[" else sbHost[1:-1];
  
  ### Port #####################################################################
  @property
  def uPortNumber(oSelf) -> int:
    return oSelf.__u0PortNumber if oSelf.__u0PortNumber is not None else gdtxDefaultPortNumberAndSecure_by_sbProtocol[oSelf.__sbProtocol][0];
  @property
  def u0PortNumber(oSelf) -> int | None:
    return oSelf.__u0PortNumber;
  @uPortNumber.setter
  def uPortNumber(oSelf,
    uPortNumber: int = None,
  ):
    assert isinstance(u0PortNumber, int) and 0 <= u0PortNumber <= 0xFFFF, \
        "uPortNumber an int in range [0-65,535], not %s" % repr(u0PortNumber);
    oSelf.__u0PortNumber = uPortNumber;
  @u0PortNumber.setter
  def u0PortNumber(oSelf,
    u0PortNumber: int | None = None,
  ):
    assert u0PortNumber is None or (isinstance(u0PortNumber, int) and 0 <= u0PortNumber <= 0xFFFF), \
        "u0PortNumber must be None or an int in range [0-65,535], not %s" % repr(u0PortNumber);
    oSelf.__u0PortNumber = u0PortNumber;
  
  ### Path #####################################################################
  # path getter and setter
  @property
  def sbPath(oSelf) -> bytes:
    return oSelf.__sbPath;
  @sbPath.setter
  def sbPath(oSelf,
    sbPath: bytes,
  ):
    assert (grbInvalidPath if oSelf.bAllowInvalidURLs else grbPath).match(sbPath), \
        "sbPath is not a valid path (%s)" % (repr(sbPath),);
    # Automatically add "/" prefix if missing.
    oSelf.__sbPath = (b"/" if (sbPath[:1] != b"/") else b"") + sbPath;
  
  # URL decoded path getter and setter
  @property
  def sPath(oSelf) -> str:
    return fsURLDecode(oSelf.__sbPath);
  @sPath.setter
  def sPath(oSelf,
    sPath: str,
  ):
    oSelf.sbPath = fsbURLEncode(sPath);
  
  # URL decoded path array getter
  @property
  def asPath(oSelf) -> list[str]:
    # "/A/B//C%2F%44/" => ["A", "B", "C", "D"]
    return [s for s in oSelf.sPath.split("/") if s] if oSelf.__sbPath != b"/" else [];
  @asPath.setter
  def asPath(oSelf,
    asPath: list[str],
  ):
    oSelf.sPath = [s for s in sPath.split("/") if s];
  
  ### Query ####################################################################
  # query getter and setter
  @property
  def sb0Query(oSelf) -> bytes | None:
    return oSelf.__sb0Query;
  @sb0Query.setter
  def sb0Query(oSelf,
    sb0Query: bytes | None,
  ):
    if sb0Query is not None:
      assert (grbInvalidQuery if oSelf.bAllowInvalidURLs else grbQuery).match(sb0Query), \
          "sb0Query is not a valid query (%s)" % (repr(sb0Query),);
    oSelf.__sb0Query = sb0Query;
  
  # URL decoded query getter and setter
  @property
  def s0Query(oSelf) -> str | None:
    return fsURLDecode(oSelf.__sb0Query) if oSelf.__sb0Query is not None else None;
  @property
  def sQuery(oSelf):
    raise NotImplementedError(
      "Please use s0Query to read the value, as it might be None. Use sQuery only to set it."
    );
  @sQuery.setter
  def sQuery(oSelf,
    sQuery: str,
  ):
    sbQuery = fsbURLEncode(sQuery);
    assert (grbInvalidQuery if oSelf.bAllowInvalidURLs else grbQuery).match(sbQuery), \
        "sQuery (%s) does not encode to a valid query (%s)" % (repr(sQuery), repr(sbQuery));
    oSelf.__sb0Query = sbQuery;
  
  # query dictionary getter and setter
  @property
  def ds0QueryValue_by_sName(oSelf) -> dict[str, str | None]:
    return fdxURLDecodedNameValuePairs(oSelf.__sb0Query) if oSelf.__sb0Query else {};
  @ds0QueryValue_by_sName.setter
  def ds0QueryValue_by_sName(oSelf,
    ds0QueryValue_by_sName: dict[str, str | None],
  ):
    oSelf.__sb0Query = fsbURLEncodedNameValuePairs(ds0QueryValue_by_sName);
  
  # query values get and set
  def fs0GetQueryValue(oSelf,
    sName: str,
  ) -> str | None:
    return oSelf.ds0QueryValue_by_sName.get(sName);
  def fSetQueryValue(oSelf,
    sName: str,
    s0Value: str | None,
  ):
    ds0QueryValue_by_sName = oSelf.ds0QueryValue_by_sName;
    ds0QueryValue_by_sName[sName] = s0Value;
    oSelf.ds0QueryValue_by_sName = ds0QueryValue_by_sName;
  
  ### Fragment #################################################################
  # fragment getter and setter
  @property
  def sb0Fragment(oSelf) -> bytes | None:
    return oSelf.__sb0Fragment;
  @sb0Fragment.setter
  def sb0Fragment(oSelf,
    sb0Fragment: bytes | None,
  ):
    oSelf.__sb0Fragment = sb0Fragment;
  # URL decoded fragment getter and setter
  @property
  def s0Fragment(oSelf) -> str | None:
    return fsURLDecode(oSelf.__sb0Fragment) if oSelf.__sb0Fragment is not None else None;
  @property
  def sFragment(oSelf):
    raise NotImplementedError(
      "Please use s0Fragment to read the value, as it might be None. Use sFragment only to set it."
    );
  @sFragment.setter
  def sFragment(oSelf,
    sFragment: str,
  ):
    sbFragment = fsbURLEncode(sFragment);
    assert grbFragment.match(sbFragment), \
        "sbFragment is not a valid fragment (%s)" % (repr(sbFragment),);
    oSelf.__sb0Fragment = sbFragment;
  
  ### Convenience ##############################################################
  @property
  def sbAddress(oSelf) -> bytes:
    if grbIPv6Address.match(oSelf.__sbHost):
      return b"[%s]:%d" % (oSelf.__sbHost, oSelf.uPortNumber);
    return b"%s:%d" % (oSelf.__sbHost, oSelf.uPortNumber);

  @property
  def sbHostAndOptionalPort(oSelf) -> bytes:
    sbHostAndOptionalPort = b"";
    if grbIPv6Address.match(oSelf.__sbHost):
      sbHostAndOptionalPort += b"[%s]" % oSelf.__sbHost;
    else:
      sbHostAndOptionalPort += oSelf.__sbHost;
    
    if oSelf.__u0PortNumber not in [None, gdtxDefaultPortNumberAndSecure_by_sbProtocol[oSelf.__sbProtocol][0]]:
      sbHostAndOptionalPort += b":%d" % oSelf.__u0PortNumber;
    return sbHostAndOptionalPort;

  @property
  def sbAuthority(oSelf) -> bytes:
    if oSelf.__sb0Username is None and oSelf.__sb0Password is None:
      sbUserInfo = b""; # some components are optional, we'll add them as needed:
    else:
      sbUserInfo = oSelf.__sb0Username or b"";
      if oSelf.__sb0Password is not None:
        sbUserInfo += b":" + oSelf.__sb0Password;
      sbUserInfo += b"@";
    return sbUserInfo + oSelf.sbHostAndOptionalPort;
  
  @property
  def oBase(oSelf) -> "cURL":
    return cURL(sbProtocol = oSelf.__sbProtocol, sbHost = oSelf.__sbHost, u0PortNumber = oSelf.__u0PortNumber);
  
  @property
  def sbBase(oSelf) -> bytes:
    return b"%s://%s" % (oSelf.__sbProtocol, oSelf.sbHostAndOptionalPort);
  
  @property
  def sbOrigin(oSelf) -> bytes:
    return b"%s://%s" % (oSelf.__sbProtocol, oSelf.sbAddress);
  
  @property
  def sbRelative(oSelf) -> bytes:
    return b"".join([
      oSelf.__sbPath,
      (b"?" + oSelf.__sb0Query) if oSelf.__sb0Query is not None else b"",
      (b"#" + oSelf.__sb0Fragment) if oSelf.__sb0Fragment is not None else b"",
    ]);
  @property
  def sbAbsolute(oSelf) -> bytes:
    return oSelf.sbBase + oSelf.sbRelative;

  def fsbSerialize(oSelf) -> str:
    return oSelf.sbAbsolute;

  def fsSerialize(oSelf) -> str:
    return str(oSelf.fsbSerialize(), 'ascii', 'strict');
  
  def fbIsValid(oSelf) -> bool:
    # returns true as long as the serialized URL is technically valid, even
    # if the individual components stored in the various properties of the
    # object are not. Returning True means that if you serialize and deserialize
    # the object, you would get a cURL instance with valid properties, which
    # may differ from this object.
    return grbURL.match(oSelf.fsbSerialize()) is not None;

  def fasGetDetails(oSelf) -> list[str]:
    return [
      "sbProtocol: %s" % repr(oSelf.__sbProtocol)[1:],
      "sb0Username: %s" % repr(oSelf.__sb0Username)[1:],
      "sb0Password: %s" % repr(oSelf.__sb0Password)[1:],
      "sbHost: %s" % repr(oSelf.__sbHost)[1:],
      "u0PortNumber: %s" % repr(oSelf.__u0PortNumber)[1:],
      "sbPath: %s" % repr(oSelf.__sbPath)[1:],
      "sb0Query: %s" % repr(oSelf.__sb0Query)[1:],
      "sb0Fragment: %s" % repr(oSelf.__sb0Fragment)[1:],
    ];
  
  def __str__(oSelf) -> str:
    return "%s{%s}" % (oSelf.__class__.__name__, str(oSelf.sbAbsolute, 'ascii', 'strict'));
  
  def __repr__(oSelf) -> str:
    return "".join([
      "<",
      oSelf.__class__.__module__,
      ".",
      oSelf.__class__.__name__,
      " ",
      repr(oSelf.__sbProtocol)[1:],
      "://",
      ("%s%s@" % (
        repr(oSelf.__sb0Username)[1:] if oSelf.__sb0Username is not None else "",
        (":%s" % repr(oSelf.__sb0Password)[1:]) if oSelf.__sb0Password is not None else "",
      )) if oSelf.__sb0Username is not None or oSelf.__sb0Password is not None else "",
      repr(oSelf.__sbHost)[1:],
      (":%s" % repr(oSelf.__u0PortNumber)) if oSelf.__u0PortNumber is not None else "",
      repr(oSelf.__sbPath)[1:],
      ("?%s" % repr(oSelf.__sb0Query)[1:]) if oSelf.__sb0Query is not None else "",
      ("#%s" % repr(oSelf.__sb0Fragment)[1:]) if oSelf.__sb0Fragment is not None else "",
      ">",
    ]);

