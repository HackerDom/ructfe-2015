#/bin/bash
cd `dirname $0` >/dev/null 2>&1
exec mono ElectroChecker.exe "$@"
