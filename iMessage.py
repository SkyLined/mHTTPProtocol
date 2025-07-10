import base64, json;

try: # mDebugOutput use is Optional
  from mDebugOutput import ShowDebugOutput, fShowDebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  ShowDebugOutput = lambda fx: fx; # NOP
  fShowDebugOutput = lambda x, s0 = None: x; # NOP

from mNotProvided import (
  fAssertTypes,
  fbIsProvided,
  fxGetFirstProvidedValue,
  zNotProvided,
);

from .fdxDecodedFormNameValuePairs import fdxDecodedFormNameValuePairs;
from .fsEncodedFormNameValuePairs import fsEncodedFormNameValuePairs;
from .mCharacterEncoding import (
  fsbCharacterEncodeDataUsingCharsetValue,
  fsCharacterDecodeDataUsingCharsetValue,
);
from .mCompression import (
  asbSupportedCompressionTypes,
  fsbCompressDataUsingCompressionTypes,
  fsbDecompressDataUsingCompressionTypes,
  ftxDecompressDataUsingExpectedCompressionTypesAndGetActualCompressionTypes,
);
from .mChunkedEncoding import (
  cChunkedData,
);
from .mExceptions import cInvalidMessageException;
from .mHeadersTrailers import cHeaders;


class iMessage(object):
  sbDefaultVersion = b"HTTP/1.1";
  ddDefaultHeader_sbValue_by_sbName_by_sbHTTPVersion = None;
  asbSupportedCompressionTypes = asbSupportedCompressionTypes;
  asbSupportedDecompressionTypes = asbSupportedCompressionTypes;
  
  @classmethod
  def foDeserialize(cClass,
    sbData: bytes,
  ) -> "iMessage":
    fAssertTypes({
      "sbData": (sbData, bytes),
    });
    # The start line and headers are separated from the body by an empty line;
    # use this to split them:
    asbStartAndHeaderLinesAndBody = sbData.split(b"\r\n\r\n", 1);
    if len(asbStartAndHeaderLinesAndBody) != 2:
      raise cInvalidMessageException(
        "The message does not contain an empty line to signal the end of the headers.",
        sbData = sbData,
      );
    (sbStartAndHeaderLines, sbBody) = asbStartAndHeaderLinesAndBody;
    # The start line and headers are separated by CRLF; use this to split them:
    asbStartLineAndHeaderLines = sbStartAndHeaderLines.split(b"\r\n");
    # The first line is the start line, the rest are headers:
    sbStartLine = asbStartLineAndHeaderLines.pop(0);
    asbHeaderLines = asbStartLineAndHeaderLines;
    # Deserialize the start line based on the type of message (request/response)
    dxConstructorArguments = cClass.fdxDeserializeStartLine(
      sbStartLine,
      bStrictErrorChecking = bStrictErrorChecking,
    );
    # Deserialize the headers:
    dxConstructorArguments["o0zHeaders"] = cHeaders.foDeserializeLines(
      asbHeadersLines,
    );
    dxConstructorArguments["sbBody"] = sbBody;
    return cClass(**dxConstructorArguments);
  
  @staticmethod
  @ShowDebugOutput
  def fdxDeserializeStartLine(
    sbStartLine: bytes,
  ) -> dict:
    raise NotImplementedError();
  
  @ShowDebugOutput
  def __init__(oSelf,
    *,
    sbzVersion: bytes | type(zNotProvided) = zNotProvided,
    o0zHeaders: cHeaders | None | type(zNotProvided) = zNotProvided,
    sbBody: bytes | None = b"",
    bSetContentLengthHeader: bool = False,
  ):
    fAssertTypes({
      "sbzVersion": (sbzVersion, bytes, zNotProvided),
      "o0zHeaders": (o0zHeaders, cHeaders, zNotProvided),
      "sbBody": (sbBody, bytes, None),
    });
    sbBody = sbBody or b""; # Ensure we have a bytes object, not None.
    oSelf.sbVersion = fxGetFirstProvidedValue(sbzVersion, oSelf.sbDefaultVersion);
    
    if fbIsProvided(o0zHeaders):
      oSelf.oHeaders = o0zHeaders or cHeaders();
    else:
      d0DefaultHeader_sbValue_by_sbName = oSelf.ddDefaultHeader_sbValue_by_sbName_by_sbHTTPVersion.get(oSelf.sbVersion);
      assert d0DefaultHeader_sbValue_by_sbName, \
          "No default headers are defined for HTTP version %s." % oSelf.sbVersion;
      oSelf.oHeaders = cHeaders.foFromDict(d0DefaultHeader_sbValue_by_sbName);
        
    oSelf.fSetBody(
      sbBody,
      bSetContentLengthHeader = bSetContentLengthHeader,
    );
  
  @ShowDebugOutput
  def foClone(oSelf, **dxOverwrittenConstructorArguments) -> "iMessage":
    dxConstructorArguments = oSelf.fdxGetCloneConstructorArguments(**dxOverwrittenConstructorArguments);
    return oSelf.__class__(**dxConstructorArguments);
  def fdxGetCloneConstructorArguments(oSelf, **dxOverwrittenConstructorArguments) -> dict:
    dxConstructorArguments = dict(dxOverwrittenConstructorArguments);
    # Add any required constructor arguments for a clone that have not been overwritten:
    if "sbzVersion" not in dxConstructorArguments:
      dxConstructorArguments["sbzVersion"] = oSelf.sbVersion;
    if "o0zHeaders" not in dxConstructorArguments:
      dxConstructorArguments["o0zHeaders"] = oSelf.oHeaders.foClone();
    if "sbBody" not in dxConstructorArguments:
      dxConstructorArguments["sbBody"] = oSelf.__sbBody;
    return dxConstructorArguments;

  ## Content-Length HEADERS ####################################################
  def fbHasContentLengthHeader(oSelf,
  ) -> bool:
    return oSelf.oHeaders.fbHasValueForNormalizedName(
      b"Content-Length",
    );
  def fSetContentLengthHeader(oSelf,
    uContentLength: int,
  ):
    fAssertTypes({
      "uContentLength": (uContentLength, int),
    });
    oSelf.oHeaders.foReplaceOrAddUniqueNameAndValue(
      b"Content-Length",
      b"%d" % uContentLength,
    );
  def fbRemoveContentLengthHeaders(oSelf,
  ):
    oSelf.oHeaders.fbRemoveForNormalizedName(
      b"Content-Length",
    );
  ## Connection: close HEADERS #################################################
  def fbHasConnectionCloseHeader(oSelf,
  ) -> bool:
    return oSelf.oHeaders.fbHasCommaSeparatedValueForNormalizedName(
      b"Connection",
      b"close"
    );
  def fSetConnectionCloseHeader(oSelf,
  ):
    oSelf.oHeaders.fbRemoveCommaSeparatedValueForNormalizedName(
      b"Connection",
      b"keep-alive",
    );
    oSelf.oHeaders.fReplaceOrAddUniqueCommaSeparatedValueForNormalizedName(
      b"Connection",
      b"close",
    );
  def fbRemoveConnectionCloseHeaders(oSelf,
  ):
    return oSelf.oHeaders.fbRemoveCommaSeparatedValueForNormalizedName(
      b"Connection",
      b"close",
    );
  ## Transfer-Encoding: chunked HEADERS #####################################
  @ShowDebugOutput
  def fbHasChunkedEncodingHeader(oSelf,
  ) -> bool:
    return oSelf.oHeaders.fbHasCommaSeparatedValueForNormalizedName(
      b"Transfer-Encoding",
      b"chunked"
    );
  @ShowDebugOutput
  def fSetChunkedEncodingHeader(oSelf,
  ) -> bool:
    oSelf.oHeaders.fReplaceOrAddUniqueCommaSeparatedValueForNormalizedName(
      b"Transfer-Encoding",
      b"chunked",
    );
  @ShowDebugOutput
  def fRemoveChunkedEncodingHeaders(oSelf,
  ) -> bool:
    return oSelf.oHeaders.fbRemoveCommaSeparatedValueForNormalizedName(
      b"Transfer-Encoding",
      b"chunked",
    );

  ## Compression HEADERS #####################################
  @ShowDebugOutput
  def fbHasCompressionHeaders(oSelf,
  ) -> bool:
    # https://www.iana.org/assignments/http-parameters/http-parameters.xhtml
    aoContentEncodingHeaders = oSelf.oHeaders.faoGetForNormalizedName(
      b"Content-Encoding",
    );
    for oHeader in aoContentEncodingHeaders:
      for sbValue in oHeader.asbCommaSeparatedValues:
        if sbValue.lower() != b"identity":
          return True;
    aoTransferEncodingHeaders = oSelf.oHeaders.faoGetForNormalizedName(
      b"Transfer-Encoding",
    );
    for oHeader in aoTransferEncodingHeaders:
      for sbValue in oHeader.asbCommaSeparatedValues:
        # "identity" is deprecated but added for backwards compatibility.
        if sbValue.lower() not in [b"chunked", "identity"]:
          return True;
    return False;
  @ShowDebugOutput
  def fasbGetCompressionTypes(oSelf,
  ) -> list[bytes]:
    return oSelf.fasbGetTransferCompressionTypes() + oSelf.fasbGetContentCompressionTypes();
  @ShowDebugOutput
  def fasbGetTransferCompressionTypes(oSelf,
  ) -> list[bytes]:
    aoTransferEncodingHeaders = oSelf.oHeaders.faoGetForNormalizedName(
      b"Transfer-Encoding",
    );
    asbCompressionTypes = [];
    for oHeader in aoTransferEncodingHeaders:
      asbCompressionTypes += [
        sbValue.lower()
        for sbValue in oHeader.asbCommaSeparatedValues
        # "identity" is deprecated but added for backwards compatibility.
        if sbValue.lower() not in [b"chunked", "identity"]
      ];
    return asbCompressionTypes;
  @ShowDebugOutput
  def fasbGetContentCompressionTypes(oSelf,
  ) -> list[bytes]:
    aoContentEncodingHeaders = oSelf.oHeaders.faoGetForNormalizedName(
      b"Content-Encoding",
    );
    asbCompressionTypes = [];
    for oHeader in aoContentEncodingHeaders:
      asbCompressionTypes += [
        sbValue.lower()
        for sbValue in oHeader.asbCommaSeparatedValues
        if sbValue.lower() != b"identity"
      ];
    return asbCompressionTypes;
  @ShowDebugOutput
  def fSetContentCompressionHeader(oSelf,
    asbCompressionTypes: list[bytes],
    bRemoveTransferCompressionHeaders: bool = False,
  ) -> bool:
    fAssertTypes({
      "asbCompressionTypes": (asbCompressionTypes, [bytes]),
      "bRemoveTransferCompressionHeaders": (bRemoveTransferCompressionHeaders, bool),
    });
    oSelf.oHeaders.foReplaceOrAddUniqueNameAndValue(
      b"Content-Encoding",
      b",".join(asbCompressionTypes),
    );
    if bRemoveTransferCompressionHeaders:
      oSelf.fbRemoveTransferCompressionHeaders();
  @ShowDebugOutput
  def fSetTransferCompressionHeader(oSelf,
    asbCompressionTypes: list[bytes],
    bRemoveContentCompressionHeaders: bool = False,
  ) -> bool:
    fAssertTypes({
      "asbCompressionTypes": (asbCompressionTypes, [bytes]),
      "bRemoveContentCompressionHeaders": (bRemoveContentCompressionHeaders, bool),
    });
    asbTransferEncodingValues = asbCompressionTypes;
    # We need to preserve "chunked" encoding!
    if oSelf.fbHasChunkedEncodingHeader:
      asbTransferEncodingValues.append("chunked");
    oSelf.oHeaders.foReplaceOrAddUniqueNameAndValue(
      b"Transfer-Encoding",
      b",".join(asbCompressionTypes),
    );
    if bRemoveContentCompressionHeaders:
      oSelf.fbRemoveContentCompressionHeaders();
  @ShowDebugOutput
  def fbRemoveCompressionHeaders(oSelf,
    *, 
    bRemoveIdentityHeaders: bool = True,
  ) -> bool:
    fAssertTypes({
      "bRemoveIdentityHeaders": (bRemoveIdentityHeaders, bool),
    });
    bRemoved = oSelf.fbRemoveContentCompressionHeaders(
      bRemoveIdentityHeaders = bRemoveIdentityHeaders,
    );
    if oSelf.fbRemoveTransferCompressionHeaders(
      bRemoveIdentityHeaders = bRemoveIdentityHeaders,
    ):
      bRemoved = True;
    return bRemoved;
  def fbRemoveContentCompressionHeaders(oSelf,
    *, 
    bRemoveIdentityHeaders: bool = True,
  ) -> bool:
    fAssertTypes({
      "bRemoveIdentityHeaders": (bRemoveIdentityHeaders, bool),
    });
    aoContentEncodingHeaders = oSelf.oHeaders.faoGetForNormalizedName(
      b"Content-Encoding",
    );
    bRemoved = False;
    for oHeader in aoContentEncodingHeaders:
      asbCommaSeparatedValues = oHeader.asbCommaSeparatedValues;
      asbLowerHeadersToKeep = [] if bRemoveIdentityHeaders else [b"identity"];
      asbRemainingValues = [
        sbValue
        for sbValue in asbCommaSeparatedValues
        if sbValue.lower() not in asbLowerHeadersToKeep
      ];
      if len(asbCommaSeparatedValues) != len(asbRemainingValues):
        bRemoved = True;
        if len(asbRemainingValues) == 0:
          oSelf.oHeaders.fbRemove(oHeader);
        else:
          oHeader.asbCommaSeparatedValues = asbRemainingValues;
    return bRemoved;
  def fbRemoveTransferCompressionHeaders(oSelf,
    *, 
    bRemoveIdentityHeaders: bool = True, # officially deprecated
  ) -> bool:
    fAssertTypes({
      "bRemoveIdentityHeaders": (bRemoveIdentityHeaders, bool),
    });
    aoTransferEncodingHeaders = oSelf.oHeaders.faoGetForNormalizedName(
      b"Transfer-Encoding",
    );
    bRemoved = False;
    for oHeader in aoTransferEncodingHeaders:
      asbCommaSeparatedValues = oHeader.asbCommaSeparatedValues;
      asbLowerHeadersToKeep = [b"chunked"] if bRemoveIdentityHeaders else [b"chunked", b"identity"];
      asbNonCompressionValues = [
        sbValue
        for sbValue in asbCommaSeparatedValues
        if sbValue.lower() not in asbLowerHeadersToKeep
      ];
      if len(asbCommaSeparatedValues) != len(asbNonCompressionValues):
        bRemoved = True;
        if len(asbNonCompressionValues) == 0:
          oSelf.oHeaders.fbRemove(oHeader);
        else:
          oHeader.asbCommaSeparatedValues = asbNonCompressionValues;
    return bRemoved;
  ## BODY ######################################################################
  def fbHasBody(oSelf,
  ) -> bool:
    return len(oSelf.__sbBody) > 0;
  @property
  def sbBody(oSelf,
  ) -> bytes:
    return oSelf.__sbBody;
  @sbBody.setter
  def sbBody(oSelf,
    sbData: bytes
  ):
    fAssertTypes({
      "sbData": (sbData, bytes),
    });
    oSelf.__sbBody = sbData;

  @ShowDebugOutput
  def fSetBody(oSelf,
    sbData: bytes,
    bRemoveChunkedEncodingHeaders: bool = False,
    bSetContentLengthHeader: bool = False,
    bSetConnectionCloseHeader: bool = False,
    bRemoveCompressionHeaders: bool = False,
  ):
    fAssertTypes({
      "sbData": (sbData, bytes),
      "bRemoveChunkedEncodingHeaders": (bRemoveChunkedEncodingHeaders, bool),
      "bSetContentLengthHeader": (bSetContentLengthHeader, bool),
      "bSetConnectionCloseHeader": (bSetConnectionCloseHeader, bool),
      "bRemoveCompressionHeaders": (bRemoveCompressionHeaders, bool),
    });
    oSelf.__sbBody = sbData;
    if bRemoveChunkedEncodingHeaders:
      oSelf.fRemoveChunkedEncodingHeaders();
    if bSetContentLengthHeader:
      oSelf.fSetContentLengthHeader(len(oSelf.__sbBody));
    if bSetConnectionCloseHeader:
      oSelf.fSetConnectionCloseHeader();
    if bRemoveCompressionHeaders:
      oSelf.fbRemoveCompressionHeaders();
  @ShowDebugOutput
  def fRemoveBody(oSelf,
    bRemoveChunkedEncodingHeaders: bool = False,
    bRemoveContentLengthHeaders: bool = False,
    bRemoveConnectionCloseHeaders: bool = False,
    bRemoveCompressionHeaders: bool = False,
    bRemoveContentTypeHeaders: bool = False,
  ):
    fAssertTypes({
      "bRemoveChunkedEncodingHeaders": (bRemoveChunkedEncodingHeaders, bool),
      "bSetContentLengthHeader": (bSetContentLengthHeader, bool),
      "bSetConnectionCloseHeader": (bSetConnectionCloseHeader, bool),
      "bRemoveCompressionHeaders": (bRemoveCompressionHeaders, bool),
      "bRemoveContentTypeHeaders": (bRemoveContentTypeHeaders, bool),
    });
    oSelf.__sbBody = b"";
    if bRemoveChunkedEncodingHeaders:
      oSelf.fRemoveChunkedEncodingHeaders();
    if bRemoveContentLengthHeaders:
      oSelf.fbRemoveContentLengthHeaders();
    if bRemoveConnectionCloseHeaders:
      oSelf.fbRemoveConnectionCloseHeaders();
    if bRemoveCompressionHeaders:
      oSelf.fbRemoveCompressionHeaders();
    if bRemoveContentTypeHeaders:
      oSelf.fbRemoveContentTypeHeaders();
  
  def fsbGetBody(oSelf,
  ) -> bytes:
    return oSelf.__sbBody;

  ## CHUNKED-ENCODE/-DECODE DATA ###############################################
  @ShowDebugOutput
  def fsbChunkedEncodeData(oSelf,
    *,
    asbData: list[bytes],
    dxTrailers: dict[bytes, bytes] | None = {}, # Can be None if not provided.
  ) -> bytes:
    fAssertTypes({
      "asbData": (asbData, [bytes]),
      "dxTrailers": (dxTrailers, dict),
    });
    return cChunkedData.foFromChunksData(
      asbData = asbData,
      dxTrailers = dxTrailers or {},
    ).fsbSerialize();
  def fsbOptionallyChunkedEncodeData(oSelf,
    *,
    sbData: bytes,
  ) -> bytes:
    if not oSelf.fbHasChunkedEncodingHeader():
      return sbData;
    return cChunkedData.foFromChunksData(
      asbData = [sbData],
      dxTrailers = {},
    ).fsbSerialize();
  @ShowDebugOutput
  def foChunkedDecodeData(oSelf,
    sbData: bytes,
  ) -> list[bytes]:
    fAssertTypes({
      "sbData": (sbData, bytes),
    });
    return cChunkedData.foDeserialize(
      sbData = sbData,
    );
  ## CHUNKED-ENCODE/-DECODE BODY ###############################################
  @ShowDebugOutput
  def foGetChunkedData(oSelf,
  ) -> list[bytes]:
    return cChunkedData.foDeserialize(oSelf.__sbBody);
  @ShowDebugOutput
  def fasbGetBodyChunks(oSelf,
  ) -> list[bytes]:
    return [
      oChunk.sbData
      for oChunk in oSelf.foGetChunkedData().aoChunks
    ];
  @ShowDebugOutput
  def fSetBodyChunks(oSelf,
    asbData: list[bytes],
    bSetChunkedEncodingHeader: bool = False,
    bRemoveContentLengthHeaders: bool = False,
    bRemoveConnectionCloseHeaders: bool = False,
  ):
    fAssertTypes({
      "asbData": (asbData, [bytes]),
      "bSetChunkedEncodingHeader": (bSetChunkedEncodingHeader, bool),
      "bRemoveContentLengthHeaders": (bRemoveContentLengthHeaders, bool),
      "bRemoveConnectionCloseHeaders": (bRemoveConnectionCloseHeaders, bool),
    });
    oSelf.__sbBody = oSelf.fsbChunkedEncodeData(
      asbData = asbData,
    );
    if bSetChunkedEncodingHeader:
      oSelf.fSetChunkedEncodingHeader();
    if bRemoveContentLengthHeaders:
      oSelf.fbRemoveContentLengthHeaders();
    if bRemoveConnectionCloseHeaders:
      oSelf.oHeaders.fbRemoveForNormalizedNameAndValue(
        b"Connection",
        b"Close",
      );
  @ShowDebugOutput
  def fAddBodyChunk(oSelf,
    sbData: bytes,
    bSetChunkedEncodingHeader: bool = False,
    bRemoveContentLengthHeaders: bool = False,
    bRemoveConnectionCloseHeaders: bool = False,
  ):
    fAssertTypes({
      "sbData": (sbData, bytes),
      "bSetChunkedEncodingHeader": (bSetChunkedEncodingHeader, bool),
      "bRemoveContentLengthHeaders": (bRemoveContentLengthHeaders, bool),
      "bRemoveConnectionCloseHeaders": (bRemoveConnectionCloseHeaders, bool),
    });
    # Decode existing chunks, add the new chunk, and re-encode the chunks.
    asbData = oSelf.fasbGetBodyChunks();
    asbData.append(sbData);
    oSelf.fSetBodyChunks(
      asbData = asbData,
      bSetChunkedEncodingHeader = bSetChunkedEncodingHeader,
      bRemoveContentLengthHeaders = bRemoveContentLengthHeaders,
      bRemoveConnectionCloseHeaders = bRemoveConnectionCloseHeaders,
    );
  @ShowDebugOutput
  def fsbGetOptionallyChunkedDecodedBody(oSelf,
  ) -> bytes:
    if oSelf.fbHasChunkedEncodingHeader():
      return b"".join(oSelf.fasbGetBodyChunks());
    else:
      return oSelf.__sbBody;
  ## COMPRESS/DECOMPRESS DATA ##################################################
  @ShowDebugOutput
  def fsbCompressData(oSelf,
    sbData: bytes,
  ) -> bytes:
    fAssertTypes({
      "sbData": (sbData, bytes),
    });
    return fsbCompressDataUsingCompressionTypes(
      sbData = sbData,
      asbCompressionTypes = oSelf.fasbGetCompressionTypes(),
    );
  @ShowDebugOutput
  def fsbDecompressData(oSelf,
    sbData: bytes,
  ) -> bytes:
    fAssertTypes({
      "sbData": (sbData, bytes),
    });
    return fsbDecompressDataUsingCompressionTypes(
      sbData = sbData,
      asbCompressionTypes = oSelf.fasbGetCompressionTypes(),
    );
  @ShowDebugOutput
  def ftxDecompressDataAndGetActualCompressionTypes(oSelf,
    sbData: bytes,
    bDataCanBeLessCompressed: bool = False,
    bDataCanBeMoreCompressed: bool = False,
  ) -> tuple[bytes, list[bytes]]:
    fAssertTypes({
      "sbData": (sbData, bytes),
      "bDataCanBeLessCompressed": (bDataCanBeLessCompressed, bool),
      "bDataCanBeMoreCompressed": (bDataCanBeMoreCompressed, bool),
    });
    return ftxDecompressDataUsingExpectedCompressionTypesAndGetActualCompressionTypes(
      sbData = sbData,
      asbExpectedCompressionTypes = oSelf.fasbGetCompressionTypes(),
      bDataCanBeLessCompressed = bDataCanBeLessCompressed,
      bDataCanBeMoreCompressed = bDataCanBeMoreCompressed,
    );
  ## COMPRESS/DECOMPRESS BODY ##################################################
  @ShowDebugOutput
  def fCompressAndSetBody(oSelf,
    sbData: bytes,
    bRemoveChunkedEncodingHeaders: bool = False,
    bSetContentLengthHeader: bool = False,
    bSetConnectionCloseHeader: bool = False,
  ):
    fAssertTypes({
      "sbData": (sbData, bytes),
      "bRemoveChunkedEncodingHeaders": (bRemoveChunkedEncodingHeaders, bool),
      "bSetContentLengthHeader": (bSetContentLengthHeader, bool),
      "bSetConnectionCloseHeader": (bSetConnectionCloseHeader, bool),
    });
    oSelf.fSetBody(
      sbData = oSelf.fsbCompressData(
        sbData = sbData,
        bRemoveChunkedEncodingHeaders = bRemoveChunkedEncodingHeaders,
        bSetContentLengthHeader = bSetContentLengthHeader,
        bSetConnectionCloseHeader = bSetConnectionCloseHeader,
      ),
    );
  @ShowDebugOutput
  def fsbGetOptionallyChunkedDecodedAndDecompressedBody(oSelf,
  ) -> bytes:
    return oSelf.fsbDecompressData(
      sbData = oSelf.fsbGetOptionallyChunkedDecodedBody(),
    );
  @ShowDebugOutput
  def ftxGetOptionallyChunkedDecodedAndDecompressedBodyAndActualCompressionTypes(oSelf,
  ) -> tuple[bytes, list[bytes]]:
    return oSelf.ftxDecompressDataAndGetActualCompressionTypes(
      sbData = oSelf.fsbGetOptionallyChunkedDecodedBody(),
    );
  def fasbGetActualCompressionTypes(oSelf):
    # We'll decompress the body, trying to fix errors and ignoring them if we cannot
    # to get the actual compression types as best we can.
    (
      sbDecompressedData,
      asbActualCompressionTypes,
    ) = oSelf.ftxGetOptionallyChunkedDecodedAndDecompressedBodyAndActualCompressionTypes();
    return asbActualCompressionTypes;
  ## CHARACTER-ENCODE/-DECODE DATA #############################################
  @ShowDebugOutput
  def fbIsBodyCharacterEncoded(oSelf):
    return oSelf.sb0Charset is not None and len(oSelf.sb0Charset) > 0;
  @ShowDebugOutput
  def fsbCharacterEncodeData(oSelf,
    sData: str,
  ) -> bytes:
    fAssertTypes({
      "sData": (sData, str),
    });
    return fsbCharacterEncodeDataUsingCharsetValue(
      sData = sData,
      sb0Charset = oSelf.sb0Charset,
    );
  @ShowDebugOutput
  def fsCharacterDecodeData(oSelf,
    sbData: bytes,
  ) -> str:
    fAssertTypes({
      "sbData": (sbData, bytes),
    });
    return fsCharacterDecodeDataUsingCharsetValue(
      sbData = sbData,
      sb0Charset = oSelf.sb0Charset,
    );
  ## CHARACTER-ENCODE&COMPRESS/DECOMPRESS&CHARACTER-DECODE DATA ################
  @ShowDebugOutput
  def fsbCharacterEncodeAndCompressData(oSelf,
    sData: str,
  ) -> bytes:
    fAssertTypes({
      "sData": (sData, str),
    });
    return oSelf.fsbCompressData(
      sbData = oSelf.fsCharacterDecodeData(
        sData = sData,
      )
    );
  @ShowDebugOutput
  def fsDecompressAndCharacterDecodeData(oSelf,
    sbData: bytes,
  ) -> str:
    fAssertTypes({
      "sbData": (sbData, bytes),
    }); 
    return oSelf.fsCharacterDecodeData(
      sbData = oSelf.fsbDecompressData(
        sbData = sbData,
      )
    );
  @ShowDebugOutput
  def ftxDecompressAndCharacterDecodeDataAndGetActualCompressionTypes(oSelf,
    sbData: bytes,
  ) -> tuple[str, list[bytes]]:
    fAssertTypes({
      "sbData": (sbData, bytes),
    });
    (
      sbDecompressedData,
      asbCompressionTypes,
    ) = oSelf.ftxDecompressDataAndGetActualCompressionTypes(
      sbData = sbData,
    );
    return (
      oSelf.fsCharacterDecodeData(sbDecompressedData),
      asbCompressionTypes,
    );
  ## CHARACTER-ENCODE&COMPRESS[&Chunk-ENCODE]/[CHUNKED-DECODE&]DECOMPRESS&DECODE BODY #########
  @ShowDebugOutput
  def fEncodeCompressedAndSetBody(oSelf,
    sData: str,
    bRemoveChunkedEncodingHeaders: bool = False,
    bSetContentLengthHeader: bool = False,
    bSetConnectionCloseHeader: bool = False,
  ) -> bytes:
    fAssertTypes({
      "sData": (sData, str),
      "bRemoveChunkedEncodingHeaders": (bRemoveChunkedEncodingHeaders, bool),
      "bSetContentLengthHeader": (bSetContentLengthHeader, bool),
      "bSetConnectionCloseHeader": (bSetConnectionCloseHeader, bool),
    });
    sbCharacterEncodedAndCompressedData = sbData = oSelf.fsbCompressData(
      sbData = oSelf.fsbCharacterEncodeData(
        sData = sData,
      )
    );
    if not bRemoveChunkedEncodingHeaders and oSelf.fbHasChunkedEncodingHeader():
      # If the body is chunked, we need to encode it before we can set it.
      sbBody = oSelf.fsbChunkedEncodeData(
        asbData = [sbCharacterEncodedAndCompressedData],
      );
    else:
      sbBody = sbCharacterEncodedAndCompressedData;
    oSelf.fSetBody(
      sbData = sbBody,
      bRemoveChunkedEncodingHeaders = bRemoveChunkedEncodingHeaders,
      bSetContentLengthHeader = bSetContentLengthHeader,
      bSetConnectionCloseHeader = bSetConnectionCloseHeader,
    );
  # alias for the above:
  fCompressedEncodeAndSetBody = fEncodeCompressedAndSetBody;
  @ShowDebugOutput
  def fsGetDecodedAndDecompressedBody(oSelf) -> str:
    return oSelf.fsCharacterDecodeData(
      sbData = oSelf.fsbDecompressData(
        sbData = oSelf.fsbGetOptionallyChunkedDecodedBody(),
      ),
    );
  # alias for the above:
  fsGetDecompressedAndDecodedBody = fsGetDecodedAndDecompressedBody;
  @ShowDebugOutput
  def ftxGetDecompressedAndDecodedBodyAndActualCompressionTypes(oSelf,
  ) -> tuple[str, list[bytes]]:
    (
      sbDecompressedAndOptionallyChunkedDecodedData,
      asbCompressionTypes,
    ) = oSelf.ftxDecompressDataAndGetActualCompressionTypes(
      sbData = oSelf.fsbGetOptionallyChunkedDecodedBody(),
    );
    return (
      oSelf.fsCharacterDecodeData(sbDecompressedAndOptionallyChunkedDecodedData),
      asbCompressionTypes,
    );
  # Alias for the above.
  ftxGetDecodedAndDecompressedBodyAndActualCompressionTypes = \
      ftxGetDecompressedAndDecodedBodyAndActualCompressionTypes;
  
  ## Content-Type HEADERS ######################################################
  @ShowDebugOutput
  def fbHasContentTypeHeader(oSelf,
  ) -> bool:
    return oSelf.oHeaders.fbHasValueForNormalizedName(
      b"Content-Type",
    );
  @ShowDebugOutput
  def fSetContentTypeHeader(oSelf,
    sbMediaType: bytes,
    *,
    sb0Charset: bytes | None = None,
    sb0Boundary: bytes | None = None,
  ):
    fAssertTypes({
      "sbMediaType": (sbMediaType, bytes),
      "sb0Charset": (sb0Charset, bytes, None),
      "sb0Boundary": (sb0Boundary, bytes, None),
    });
    sbHeaderValue = (
      sbMediaType +
      b"; charset=%s" % sb0Charset if sb0Charset else b"" +
      b"; boundary=%s" % sb0Boundary if sb0Boundary else b""
    );
    oSelf.oHeaders.foReplaceOrAddUniqueNameAndValue(
      b"Content-Type",
      sbHeaderValue,
    );
  @ShowDebugOutput
  def fRemoveContentTypeHeader(oSelf):
    oSelf.oHeaders.fbRemoveForNormalizedName(
      b"Content-Type",
    );
  
  @property
  @ShowDebugOutput
  def sb0MediaType(oSelf,
  ) -> bytes | None:
    aoContentTypeHeaders = oSelf.oHeaders.faoGetForNormalizedName(b"Content-Type");
    if len(aoContentTypeHeaders) != 1:
      return None;
    return  aoContentTypeHeaders[0].sbValue.split(b";")[0].strip();
  @sb0MediaType.setter
  @ShowDebugOutput
  def sb0MediaType(oSelf,
    sb0Value: bytes | None,
  ):
    fAssertTypes({
      "sb0Value": (sb0Value, bytes, None),
    });
    if sb0Value is None:
      oSelf.fRemoveContentTypeHeader();
    else:
      oSelf.fSetContentTypeHeader(sb0Value, oSelf.sb0Charset, oSelf.sb0Boundary);
  
  @property
  @ShowDebugOutput
  def sb0Charset(oSelf,
  ) -> bytes | None:
    aoContentTypeHeaders = oSelf.oHeaders.faoGetForNormalizedName(b"Content-Type");
    return len(aoContentTypeHeaders) == 1 and aoContentTypeHeaders[0].fsb0GetParameterValueForNormalizedName(b"charset");
  @sb0Charset.setter
  @ShowDebugOutput
  def sb0Charset(oSelf,
    sb0Value: bytes | None,
  ):
    fAssertTypes({
      "sb0Value": (sb0Value, bytes, None),
    });
    assert oSelf.sb0MediaType, \
        "Cannot set charset without a media type.";
    oSelf.__fSetContentTypeHeader(oSelf.sb0MediaType, sb0Value, oSelf.sb0Boundary);
  
  @property
  @ShowDebugOutput
  def sb0Boundary(oSelf,
  ) -> bytes | None:
    aoContentTypeHeaders = oSelf.oHeaders.faoGetForNormalizedName(b"Content-Type");
    return len(aoContentTypeHeaders) == 1 and aoContentTypeHeaders[0].fsb0GetParameterValueForNormalizedName(b"boundary");
  @sb0Boundary.setter
  @ShowDebugOutput
  def sb0Boundary(oSelf,
    sb0Value: bytes,
  ):
    fAssertTypes({
      "sb0Value": (sb0Value, bytes),
    });
    assert oSelf.sb0MediaType, \
        "Cannot set boundary without a media type.";
    oSelf.__fSetContentTypeHeader(oSelf.sb0MediaType, oSelf.sb0Charset, sb0Value);
  
  ## application/x-www-form-urlencoded Media Type ##############################
  @property
  @ShowDebugOutput
  def ds0FormValue_by_sName(oSelf) -> dict[str, str | None]:
    return fdxDecodedFormNameValuePairs(
      sData = oSelf.fsGetDecodedAndDecompressedBody(),
    );
  def ds0NormalizedFormValue_by_sNormalizedName(oSelf) -> dict[str, str | None]:
    return dict([
      (
        sName.strip().lower(),
        s0Value.strip().lower() if s0Value is not None else None,
      )
      for (sName, s0Value) in oSelf.ds0FormValue_by_sName.items()
    ]);

  @ds0FormValue_by_sName.setter
  @ShowDebugOutput
  def ds0FormValue_by_sName(oSelf,
    ds0FormValue_by_sName: dict[str, str | None]
  ):
    fAssertTypes({
      "ds0FormValue_by_sName": (ds0FormValue_by_sName, dict),
    });
    if not oSelf.fbHasContentTypeHeader():
      oSelf.fSetContentTypeHeader(
        sbMediaType = b"application/x-www-form-urlencoded",
        sb0Charset = None,
        sb0Boundary = None,
      );    sData = fsEncodedFormNameValuePairs(ds0FormValue_by_sName);
    oSelf.fEncodeCompressedAndSetBody(
      sData,
      bSetContentLengthHeader = (
        oSelf.fbHasContentLengthHeader()
        or (not oSelf.fbHasConnectionCloseHeader() and not oSelf.fbHasChunkedEncodingHeader())
      ),
    );
  def fSetFormValue(oSelf,
    sName: str,
    s0Value: str | None,
  ):
    ds0FormValue_by_sName = oSelf.ds0FormValue_by_sName;
    ds0FormValue_by_sName[sName] = s0Value;
    oSelf.ds0FormValue_by_sName = ds0FormValue_by_sName;
  @ShowDebugOutput
  def fRemoveFormValue(oSelf, sName):
    oSelf.fSetFormValue(sName, None);
  
  ## application/json Media-Type ###############################################
  @property
  @ShowDebugOutput
  def d0JSON_sValue_by_sName(oSelf):
    # convert the decoded and decompressed body to form name-value pairs.
    sb0MediaType = oSelf.sb0MediaType;
    if sb0MediaType is None or sb0MediaType.lower() != b"application/json":
      return None;
    s0Data = oSelf.fs0GetData(bRemoveCompression = True);
    if s0Data is None:
      return None;
    try:
      xJSONData = json.parse(s0Data);
    except ValueError:
      return None;
    if not isinstance(xJSONData, dict):
      return None;
    return xJSONData;

  @ShowDebugOutput
  def fs0GetJSONValue(oSelf,
    sName: str,
  ) -> str | None:
    fAssertTypes({
      "sName": (sName, str),
    });
    # convert the decoded and decompressed body to form name-value pairs and return the value for the given name
    # or None if there is no such value.
    d0JSON_sValue_by_sName = oSelf.d0JSON_sValue_by_sName;
    if d0JSON_sValue_by_sName is None or not isinstance(dForm_sValue_by_sName, dict):
      return None;
    dForm_sValue_by_sName = d0JSON_sValue_by_sName;
    return dForm_sValue_by_sName.get(sName);
  
  @ShowDebugOutput
  def fSetJSONValue(oSelf,
    sName: str,
    xValue: str | float | bool | list | dict | None,
  ):
    fAssertTypes({
      "sName": (sName, str),
      "xValue": (xValue, str, float, bool, list, dict, None),
    });
    # Convert the decoded and decompressed body to form name-value pairs,
    # remove all existing values with the given name,
    # if the value is not None, add the new named value,
    # and update the optionally compressed body to match.
    d0JSON_sValue_by_sName = oSelf.d0JSON_sValue_by_sName;
    if d0JSON_sValue_by_sName is None:
      oSelf.fSetContentTypeHeader(
        sbMediaType = b"application/json",
        sb0Charset = b"utf-8",
        sb0Boundary = None
      );
      dJSON_sValue_by_sName = {};
    else:
      dJSON_sValue_by_sName = d0JSON_sValue_by_sName;
    dJSON_sValue_by_sName[sName] = xValue;
    sData = json.dumps(dJSON_sValue_by_sName);
    oSelf.fEncodeCompressedAndSetBody(
      sData,
      bSetContentLengthHeader = (
        oSelf.fbHasContentLengthHeader()
        or (not oSelf.fbHasConnectionCloseHeader() and not oSelf.fbHasChunkedEncodingHeader())
      ),
    );
  
  ## Authorization HEADER ######################################################
  @ShowDebugOutput
  def ftsb0GetBasicAuthorization(oSelf):
    sb0Authorization = oSelf.oHeaders.fs0GetUniqueHeaderValue(b"Authorization");
    if sb0Authorization is None:
      return (None, None);
    sbBasic, sbBase64EncodedUserNameColonPassword = sb0Authorization.strip().split(b" ", 1);
    if sbBasic.lower() != b"basic ":
      return (None, None);
    try:
      sbUserNameColonPassword = base64.b64decode(sbBase64EncodedUserNameColonPassword.lstrip());
    except binascii.Error:
      return (None, None);
    if b":" in sbUserNameColonPassword:
      sbUserName, sbPassword = sbUserNameColonPassword.split(":", 1);
    else:
      sbUserName = sbUserNameColonPassword;
      sbPassword = None;
    return (sbUserName, sbPassword);
  
  @ShowDebugOutput
  def fSetBasicAuthorization(oSelf,
    sbUserName: bytes,
    sbPassword: bytes,
  ):
    fAssertTypes({
      "sbUserName": (sbUserName, bytes),
      "sbPassword": (sbPassword, bytes),
    });
    sbBase64EncodedUserNameColonPassword = base64.b64encode("%s:%s" % (sbUserName, sbPassword));
    oSelf.oHeaders.fbReplaceOrAddUniqueHeaderForNameAndValue(
      b"Authorization",
      b"basic %s" % sbBase64EncodedUserNameColonPassword,
    );
  
  def fsbSerialize(oSelf):
    sbStartLine = oSelf.fsbGetStartLine() + b"\r\n";
    sbHeaders = oSelf.oHeaders.fsbSerialize();
    return sbStartLine + sbHeaders + b"\r\n" + oSelf.__sbBody;
  
  def fasGetDetails(oSelf):
    # Make sure not to call *any* method that has ShowDebugOutput, as this causes
    # fasGetDetails to get called again, resulting in infinite recursion.
    if hasattr(oSelf, "oHeaders"):
      s0NumberOfHeaders = "%d headers" % oSelf.oHeaders.uNumberOfHeaders;
    else:
      s0NumberOfHeaders = None;
    try:
      sbBody = oSelf.__sbBody;
    except:
      s0Body = None;
    else:
      if len(sbBody) > 0:
        s0Body = f"{len(sbBody)} bytes body";
      else:
        s0Body = "no body";
    return [s for s in [
      repr(oSelf.fsbGetStartLine())[1:],
      s0NumberOfHeaders,
      s0Body,
    ] if s];
  
  def __repr__(oSelf):
    sModuleName = ".".join(oSelf.__class__.__module__.split(".")[:-1]);
    return "<%s.%s#%X|%s>" % (sModuleName, oSelf.__class__.__name__, id(oSelf), "|".join(oSelf.fasGetDetails()));
  
  def __str__(oSelf):
    return "%s#%X{%s}" % (oSelf.__class__.__name__, id(oSelf), ", ".join(oSelf.fasGetDetails()));
