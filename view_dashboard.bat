@echo off
REM MdMax Dashboard Viewer
REM Atalho para visualizar o dashboard com as 5 melhorias

if "%1%"=="html" (
    echo Abrindo dashboard HTML...
    python "%~dp0scripts\dashboard_advanced.py" html
    start /B explorer "%USERPROFILE%\markdown\exports\mdmax_dashboard_advanced.html"
) else (
    echo Mostrando dashboard do console...
    python "%~dp0scripts\dashboard_advanced.py"
    pause
)
