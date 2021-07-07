import urllib.parse;

def fdsURLDecodedNameValuePairsFromBytesString(sbData, bUseFirstValueForDuplicates = True):
  dsValue_by_sName = {};
  for sbEncodedNameValuePair in sbData.split(b"&"):
    sbEncodedName, sbEncodedValue = sbEncodedNameValuePair.split(b"=", 1) if b"=" in sbEncodedNameValuePair else (sbEncodedNameValuePair, None);
    sName = urllib.parse.unquote(sbEncodedName);
    if sName not in dsValue_by_sName or not bUseFirstValueForDuplicates:
      sValue = urllib.parse.unquote(sbEncodedValue);
      dsValue_by_sName[sName] = sValue;
  return dsValue_by_sName;
