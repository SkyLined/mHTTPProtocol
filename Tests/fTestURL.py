from mHTTPProtocol import cURL;
from mHTTPProtocol.mURL.cURL import grbProtocol, grbHostInURL;

def fTestURL(bRunFullTests):
  for sbProtocol in [b"http", b"https"]:
    assert grbProtocol.match(sbProtocol), \
        "grbHostInURL does not match %s" % repr(sbProtocol);
    for sbHost in [b"x", b"skylined.nl", b"1.a-z.domain", b"0.1.2.3", b"[0:1:2:3:4:5:6:7]"]:
      assert sbHost == "" or grbHostInURL.match(sbHost), \
          "grbHostInURL does not match %s" % repr(sbHost);
      for sbPath in [b"", b"/", b"/path", b"/path/with/sections"]:
        for sbQuery in [b"", b"?", b"?a", b"?a=1", b"?a=1&b=2", b"?a=1&a=2"]:
          for sbHash in [b"", b"#", b"#hash"]:
            sbURL = sbProtocol + b"://" + sbHost + sbPath + sbQuery + sbHash;
            oURL = cURL.foFromBytesString(sbURL);
