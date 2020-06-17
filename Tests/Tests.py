from fTestDependencies import fTestDependencies;
fTestDependencies();

from mDebugOutput import fEnableDebugOutputForClass, fEnableDebugOutputForModule, fTerminateWithException;
try:
  # Testing is currently extremely rudimentary.
  from fTestURL import fTestURL;
  fTestURL();
except Exception as oException:
  fTerminateWithException(oException, bShowStacksForAllThread = True);
