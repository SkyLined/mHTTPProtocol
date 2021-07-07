import urllib.parse;

def fsbURLEncodedNameValuePairsToBytesString(dsValue_by_sName):
  asbData = [];
  for (sName, sValue) in dsValue_by_sName.items():
    sbData = bytes(urllib.parse.quote(sName), "latin1");
    if sValue is not None:
      sbData += b"=" + bytes(urllib.parse.quote(sValue), 'latin1');
    asbData.append(sbData);
  return b"&".join(asbData);
