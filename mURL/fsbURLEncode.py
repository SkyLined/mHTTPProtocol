import urllib.parse;

def fsbURLEncode(
  sData: str,
) -> bytes:
  return bytes(urllib.parse.quote(sData), "ascii", "strict");
