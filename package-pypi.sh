#!/bin/sh -ex

PYTHON=${PYTHON:-python}

rm -rf pypi/yowasp_silice/share

cp README.md pypi/README.md
cp silice-prefix/bin/silice silice-prefix/bin/silice.wasm
cp silice-src/bin/silice-make.py silice-prefix/bin/silice_make.py
cp silice-src/bin/report-cycles.py silice-prefix/bin/report_cycles.py

cp -r \
  silice-prefix/bin/silice.wasm \
  silice-prefix/bin/silice_make.py \
  silice-prefix/bin/report_cycles.py \
  silice-prefix/share \
  pypi/yowasp_silice/

cd pypi
rm -rf build

${PYTHON} -m build -w
sha256sum dist/*.whl
