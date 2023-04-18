import urllib.parse;

from mNotProvided import fAssertTypes;

def fsbURLEncodedNameValuePairsToBytesString(dsValue_by_sName):
  fAssertTypes({
    "dsValue_by_sName": (dsValue_by_sName, {str: str}),
  });
  asbData = [];
  for (sName, sValue) in dsValue_by_sName.items():
    fAssertTypes({
      "sName": (sName, str),
      "sValue": (sValue, str),
    });
    sbData = bytes(urllib.parse.quote(sName), "ascii", "strict");
    if sValue is not None:
      sbData += b"=" + bytes(urllib.parse.quote(sValue), "ascii", "strict");
    asbData.append(sbData);
  return b"&".join(asbData);
