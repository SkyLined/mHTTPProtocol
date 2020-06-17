try: # mDebugOutput use is Optional
  from mDebugOutput import *;
except: # Do nothing if not available.
  ShowDebugOutput = lambda fxFunction: fxFunction;
  fShowDebugOutput = lambda sMessage: None;
  fEnableDebugOutputForModule = lambda mModule: None;
  fEnableDebugOutputForClass = lambda cClass: None;
  fEnableAllDebugOutput = lambda: None;
  cCallStack = fTerminateWithException = fTerminateWithConsoleOutput = None;

from mHTTPConnections import cURL;

def fTestURL():
  fShowDebugOutput(("\xFE\xFE\xFE\xFE Testing cURL...").ljust(160, "\xFE"));
  cURL.foFromString("http://0.1.2.3:12345/path?query#hash");
  cURL.foFromString("https://[0:1:2:3:4:5:6:7]:12345/path?query#hash");
  cURL.foFromString("http://host/path?query#hash");
  cURL.foFromString("http://a.b-c.1.domain/path?query#hash");
