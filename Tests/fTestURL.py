from mHTTPProtocol import cURL;

def fTestURL():
  cURL.foFromBytesString(b"http://0.1.2.3:12345/path?query#hash");
  cURL.foFromBytesString(b"https://[0:1:2:3:4:5:6:7]:12345/path?query#hash");
  cURL.foFromBytesString(b"http://host/path?query#hash");
  cURL.foFromBytesString(b"http://a.b-c.1.domain/path?query#hash");
