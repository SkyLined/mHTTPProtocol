from ..mExceptions import (
  cDataCannotBeDecodedWithCharsetException,
  cInvalidCharsetValueException,
  cUnhandledCharsetValueException,
);

def fsCharacterDecodeDataUsingCharsetValue(
  *,
  sbData: bytes,
  sb0Charset: bytes | None,
) -> str:
  if not sb0Charset:
    # Convert bytes to Unicode code-points.
    return "".join(chr(uByte) for uByte in sbData);
  sbCharset = sb0Charset;
  # Make sure the charset is a valid ASCII string.
  try:
    sCharset = str(sbCharset, 'ascii');
  except UnicodeError as oException:
    raise cInvalidCharsetValueException(
      "The charset %s is invalid." % repr(sbCharset)[1:],
      sbCharset = sbCharset,
    );
  # Decode the data using the charset.
  try:
    sData = str(sbData, sCharset, "strict");
  except LookupError as oException:
    raise cUnhandledCharsetValueException(
      "The charset %s is unknown." % repr(sCharset),
      sbCharset = sb0Charset,
    );
  except UnicodeError as oException:
    raise cDataCannotBeDecodedWithCharsetException(
      "The data cannot be decoded with %s encoding." % repr(sCharset),
      sbData = sbData,
      sb0Charset = sb0Charset,
    );
  return sbData;
