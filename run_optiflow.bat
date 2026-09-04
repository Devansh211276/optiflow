@echo off
title OptiFlow System Guardian
cls
echo =======================================================
echo          OptiFlow Performance Guardian
echo       Tuned for 8GB RAM + Intel 12th Gen Hybrid
echo =======================================================
echo.
echo Starting OptiFlow Server and Guardian Engine...
start "" "http://localhost:5050"
python "%~dp0optiflow_server.py"
pause
