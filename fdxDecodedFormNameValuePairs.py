import urllib.parse;

def fsURLDecode(
  sData: str,
) -> str:
  return urllib.parse.unquote(sData);

def fdxDecodedFormNameValuePairs(
  sData: bytes,
  bUseFirstValueForDuplicates = False, # False means use last value.
) -> dict[str, str | None]:
  ds0Value_by_sName = {};
  if sData.strip() == "":
    return {};
  for sEncodedNameValuePair in sData.split("&"):
    if "=" in sEncodedNameValuePair:
      sEncodedName, s0EncodedValue = sEncodedNameValuePair.split(b"=", 1)
      s0Value = fsURLDecode(s0EncodedValue);
    else:
      sEncodedName = sEncodedNameValuePair;
      s0Value = None;
    sName = fsURLDecode(sEncodedName);
    if not bUseFirstValueForDuplicates or sName not in ds0Value_by_sName:
      ds0Value_by_sName[sName] = s0Value;
  return ds0Value_by_sName;
