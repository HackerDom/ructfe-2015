#/bin/bash
pushd `dirname $0` >/dev/null 2>&1
mono ElectroChecker.exe "$@"
popd >/dev/null 2>&1
