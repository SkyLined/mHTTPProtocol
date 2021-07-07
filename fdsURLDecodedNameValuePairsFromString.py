import urllib.parse;

def fdsURLDecodedNameValuePairsFromString(sData, bUseFirstValueForDuplicates = True):
  dsValue_by_sName = {};
  for sEncodedNameValuePair in sData.split("&"):
    sEncodedName, sEncodedValue = sEncodedNameValuePair.split("=", 1) if "=" in sEncodedNameValuePair else (sEncodedNameValuePair, None);
    sName = urllib.parse.unquote(sEncodedName);
    if sName not in dsValue_by_sName or not bUseFirstValueForDuplicates:
      sValue = urllib.parse.unquote(sEncodedValue);
      dsValue_by_sName[sName] = sValue;
  return dsValue_by_sName;
