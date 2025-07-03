from ..mExceptions import (
  cDataCannotBeEncodedWithCharsetException,
  cInvalidCharsetValueException,
  cUnhandledCharsetValueException,
);

def fsbCharacterEncodeDataUsingCharsetValue(
  *,
  sData: bytes,
  sb0Charset: bytes | None,
) -> bytes:
  if not sb0Charset:
    # No charset: convert Unicode code-points to bytes if possible.
    try:
      return bytes(ord(sChar) for sChar in sData);
    except ValueError:
      raise cDataCannotBeEncodedWithCharsetException(
        "The data cannot be convert to bytes without a charset because it contains Unicode characters with code-points > 255.",
        sData = sData,
        sb0Charset = sb0Charset,
      );
  # Make sure the charset is a valid ASCII string.
  try:
    sCharset = str(sbCharset, "ascii", "strict");
  except UnicodeError as oException:
    raise cInvalidCharsetValueException(
      "The charset %s is invalid." % repr(sbCharset)[1:],
      sbCharset = sbCharset,
    );
  # Encode the data using the charset.
  try:
    sbData = bytes(sData, sCharset, "strict");
  except LookupError as oException:
    raise cUnhandledCharsetValueException(
      "The charset %s is unhandled." % repr(sCharset),
      sbCharset = sbCharset,
    );
  except UnicodeError as oException:
    raise cDataCannotBeEncodedWithCharsetException(
      "The data cannot be encoded with %s-encoded." % repr(sCharset),
      sbData = sbData,
      sb0Charset = sb0Charset,
    );
  return sbData;

