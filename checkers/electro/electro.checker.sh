#/bin/bash
cd `dirname $0` >/dev/null 2>&1
mono ElectroChecker.exe "$@"
