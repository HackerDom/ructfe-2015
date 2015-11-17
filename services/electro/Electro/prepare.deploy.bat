md %1\..\service
md %1\..\service\web

xcopy /d /y /e %1\..\..\..\static %1\..\service\web
del %1\..\service\web\service-template.html
xcopy /d /y /e %1\web %1\..\service\web

copy %2\*.exe %1\..\service\
copy %2\*.dll %1\..\service\
copy %2\*.pdb %1\..\service\
copy %2\*.config %1\..\service\
del %1\..\service\*.vshost.*