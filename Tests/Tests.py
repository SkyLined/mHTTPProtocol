import os, sys;
sModulePath = os.path.dirname(__file__);
sys.path = [sModulePath] + [sPath for sPath in sys.path if sPath.lower() != sModulePath.lower()];

from fTestDependencies import fTestDependencies;
fTestDependencies("--automatically-fix-dependencies" in sys.argv);
sys.argv = [s for s in sys.argv if s != "--automatically-fix-dependencies"];

try: # mDebugOutput use is Optional
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

guExitCodeInternalError = 1; # Use standard value;
try:
  try:
    from mConsole import oConsole;
  except:
    import sys, threading;
    oConsoleLock = threading.Lock();
    class oConsole(object):
      @staticmethod
      def fOutput(*txArguments, **dxArguments):
        sOutput = "";
        for x in txArguments:
          if isinstance(x, str):
            sOutput += x;
        sPadding = dxArguments.get("sPadding");
        if sPadding:
          sOutput.ljust(120, sPadding);
        oConsoleLock.acquire();
        print(sOutput);
        sys.stdout.flush();
        oConsoleLock.release();
      @staticmethod
      def fStatus(*txArguments, **dxArguments):
        pass;
  
  from fTestURL import fTestURL;
  from fTestCompression import fTestCompression;
  from fTestRequest import fTestRequest;
  from fTestResponse import fTestResponse;
  
  bRunFullTests = False;
  for sArgument in sys.argv[1:]:
    if sArgument == "--full":
      bRunFullTests = True;
    elif sArgument == "--debug":
      assert m0DebugOutput, \
          "m0DebugOutput module is not available";
      # Turn on debugging for various classes, including a few that are not directly exported.
      import mHTTPProtocol;
      m0DebugOutput.fEnableDebugOutputForModule(mHTTPProtocol);
    else:
      raise AssertionError("Unknown argument %s" % sArgument);

  # Test URLs
  oConsole.fOutput("\u2500\u2500\u2500 Testing cURL ", sPadding = "\u2500");
  fTestURL(bRunFullTests);
  oConsole.fOutput("+ Done.");
  
  # Test compression/decompression
  oConsole.fOutput("\u2500\u2500\u2500 Testing compression/decompression ", sPadding = "\u2500");
  fTestCompression(bRunFullTests);
  oConsole.fOutput("+ Done.");
  
  # Test requests class
  oConsole.fOutput("\u2500\u2500\u2500 Testing cHTTPRequest ", sPadding = "\u2500");
  fTestRequest(bRunFullTests);
  oConsole.fOutput("+ Done.");

  # Test response class
  oConsole.fOutput("\u2500\u2500\u2500 Testing cHTTPResponse ", sPadding = "\u2500");
  fTestResponse(bRunFullTests);
  oConsole.fOutput("+ Done.");

except Exception as oException:
  if m0DebugOutput:
    m0DebugOutput.fTerminateWithException(oException, guExitCodeInternalError, bShowStacksForAllThread = True);
  raise;
