import urllib.parse;

def fsbURLEncodedNameValuePairsToBytesString(dsValue_by_sName):
  asbData = [];
  for (sName, sValue) in dsValue_by_sName.items():
    sbData = bytes(urllib.parse.quote(sName), "ascii", "strict");
    if sValue is not None:
      sbData += b"=" + bytes(urllib.parse.quote(sValue), "ascii", "strict");
    asbData.append(sbData);
  return b"&".join(asbData);
