import sys
import yowasp_runtime
from . import silice_make

try:
    from importlib import resources as importlib_resources
    importlib_resources.files
except (ImportError, AttributeError):
    import importlib_resources

def run_silice(argv):
    print(argv)
    if "--frameworks_dir" in argv:
        cmd_argv = ["yowasp-silice", *argv]
    else:
        cmd_argv = ["yowasp-silice", "--framework","share/silice/frameworks/boards/icestick/icestick.v","--frameworks_dir","share/silice/frameworks/", *argv]
    return yowasp_runtime.run_wasm(__package__, "silice.wasm", resources=["share"], argv=cmd_argv)

def run_make(argv):
    silice_make.make(argv)

def _run_silice_argv():
    sys.exit(run_silice(sys.argv[1:]))

def _run_make_argv():
    sys.exit(run_make(sys.argv[1:]))
