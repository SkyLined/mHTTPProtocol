from .fsURLDecode import fsURLDecode;

def fdxURLDecodedNameValuePairs(
  sbData: bytes,
  bUseFirstValueForDuplicates = False, # False means use last value.
):
  ds0Value_by_sName = {};
  for sbEncodedNameValuePair in sbData.split(b"&"):
    if b"=" in sbEncodedNameValuePair:
      sbEncodedName, sb0EncodedValue = sbEncodedNameValuePair.split(b"=", 1)
    else:
      sbEncodedName = sbEncodedNameValuePair
      sb0EncodedValue = None;
    sName = fsURLDecode(sbEncodedName);
    s0Value = fsURLDecode(sb0EncodedValue) if sb0EncodedValue is not None else None;
    if not bUseFirstValueForDuplicates or sName not in ds0Value_by_sName:
      ds0Value_by_sName[sName] = s0Value;
  return ds0Value_by_sName;
