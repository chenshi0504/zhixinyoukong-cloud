@echo off
chcp 65001 >nul
echo ========================================
echo   智信优控 · 云端管理平台 启动脚本
echo ========================================
echo.

:: 启动后端 API（HTTPS，端口 8000，IPv6）
echo [1/1] 启动后端 API 服务（HTTPS）...
start "云端后端API" /D "%~dp0backend" D:\chenshi\Research\torch_env\python.exe -m uvicorn app.main:app --host :: --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem

:: 等待后端启动
timeout /t 3 /nobreak >nul

echo.
echo 启动完成！
echo   后端 API: https://[2001:da8:a800:800::8ef]:8000/api/cloud/health
echo   前端页面: https://chenshi0504.github.io/zhixinyoukong-cloud/
echo.
pause
