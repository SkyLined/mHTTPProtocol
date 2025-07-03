import urllib.parse;

def fsURLDecode(
  sbData: bytes,
) -> str:
  return urllib.parse.unquote(sbData);
