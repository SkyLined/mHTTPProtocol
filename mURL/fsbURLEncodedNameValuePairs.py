from .fsbURLEncode import fsbURLEncode;

def fsbURLEncodedNameValuePairs(
  dsValue_by_sName: dict[str, str],
) -> bytes:
  asbData = [];
  for (sName, sValue) in dsValue_by_sName.items():
    sbData = fsbURLEncode(sName);
    if sValue is not None:
      sbData += b"=" + fsbURLEncode(sValue);
    asbData.append(sbData);
  return b"&".join(asbData);
