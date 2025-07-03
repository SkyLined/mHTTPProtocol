import urllib.parse;

def fsURLEncode(
  sData: str,
) -> bytes:
  return urllib.parse.quote(sData);

def fsEncodedFormNameValuePairs(
  ds0Value_by_sName: dict[str, str | None],
) -> bytes:
  asData = [];
  for (sName, s0Value) in ds0Value_by_sName.items():
    sData = fsURLEncode(sName);
    if s0Value is not None:
      sData += "=" + fsURLEncode(s0Value);
    else:
      assert sName, repr(ds0Value_by_sName);
    asData.append(sData);
  return "&".join(asData);
