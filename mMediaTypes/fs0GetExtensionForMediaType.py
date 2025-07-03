from .dasExtensions_by_sbMediaType import dasExtensions_by_sbMediaType;

def fs0GetExtensionForMediaType(sbMediaType):
  return dasExtensions_by_sbMediaType.get(sbMediaType.lower(), [None])[0];
