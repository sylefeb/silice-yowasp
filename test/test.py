# From yowasp_runtime

import sys
import wasmtime
import threading
import os

wasi_cfg = wasmtime.WasiConfig()

# inherit standard I/O handles
wasi_cfg.inherit_stdin()
wasi_cfg.inherit_stdout()
wasi_cfg.inherit_stderr()

# wasi_cfg.argv = ["silice","blinky.si","--framework","share/silice/frameworks/boards/icestick/icestick.v","--frameworks_dir","share/silice/frameworks/"]
wasi_cfg.argv = ["silice","--help"]

# preopens for absolute paths
if os.name == "nt":
    drive_mask = ctypes.cdll.kernel32.GetLogicalDrives()
    for drive_index in range(26):
        if drive_mask & (1 << drive_index):
            drive_letter = "abcdefghijklmnopqrstuvwxyz"[drive_index]
            try:
                wasi_cfg.preopen_dir(drive_letter + ":\\", drive_letter + ":")
                drive_letter = drive_letter.upper()
                wasi_cfg.preopen_dir(drive_letter + ":\\", drive_letter + ":")
            except wasmtime.WasmtimeError:
                # drive letter present, but not accessible for some reason; ignore it
                continue
else:
    # can't do this for files, but no one's going to use yowasp on files in / anyway
    for path in os.listdir("/"):
        if os.path.isdir("/" + path):
            try:
                wasi_cfg.preopen_dir("/" + path, "/" + path)
            except wasmtime.WasmtimeError:
                # root subdirectory present, but not accessible (permission issue?); ignore
                continue

# preopens for relative paths
wasi_cfg.preopen_dir("../silice-prefix/share", "./share")
wasi_cfg.preopen_dir(".",".")

engine = wasmtime.Engine()
with open("../silice-build/silice", "rb") as f:
    module_binary = f.read()
module = wasmtime.Module(engine, module_binary)

linker = wasmtime.Linker(engine)
linker.define_wasi()

store = wasmtime.Store(engine)
store.set_wasi(wasi_cfg)

app = linker.instantiate(store, module)
linker.define_instance(store, "app", app)

# wrap Wasm function to handle traps
exception = None
def run():
    try:
        print('running')
        app.exports(store)["_start"](store)
    except Exception as e:
        exception = e

# run the application; this needs to be done in a thread other than the main thread
# because signal handlers always execute on the main thread and we won't be able
# to process SIGINT otherwise
thread = threading.Thread(target=run)
thread.daemon = True
thread.start()
thread.join()
try:
    if exception is not None:
        print('exception')
        raise exception # re-raise to preserve backtrace
except wasmtime.ExitTrap as trap:
    print('trap', trap.code)
