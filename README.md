YoWASP Silice packages
=======================

The YoWASP Silice package provides [Silice](https://github.com/sylefeb/Silice) built for [WebAssembly]() and the [YoWASP project](http://yowasp.org/).

Notes
-----

- Error reporting has limitations due to having to compile without C++ exceptions for WASI. This is in particular the case for preprocessor errors.
- The [easy-riscv](https://github.com/sylefeb/Silice/tree/master/projects/easy-riscv) feature of Silice is currently not supported as it needs to call [gcc]() externally.

Versioning
----------

The version of this package is derived from the upstream Silice package version, and is currently the git commit version.

Configuration
-------------

See the documentation for [yowasp-runtime](https://github.com/YoWASP/runtime#configuration).

License
-------

This package is covered by the [ISC license](LICENSE.txt), which is the same as the [YoWASP license](https://github.com/YoWASP/yosys/blob/develop/LICENSE.txt).

Credits
-------
- YoWASP by whitequark, see http://yowasp.org/
