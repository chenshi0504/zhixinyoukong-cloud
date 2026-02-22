@echo off
chcp 65001 >nul
echo ========================================
echo   智信优控 · 云端管理平台 启动脚本
echo ========================================
echo.

:: 启动后端 API（端口 8000）
echo [1/2] 启动后端 API 服务...
start "云端后端API" /D "%~dp0backend" D:\chenshi\Research\torch_env\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端开发服务器（端口 5173）
echo [2/2] 启动前端服务...
start "云端前端" /D "%~dp0frontend" cmd /c "npm run dev -- --host 0.0.0.0"

echo.
echo 启动完成！
echo   后端 API: http://localhost:8000/api/cloud/health
echo   前端页面: http://localhost:5173
echo   管理平台: http://[2001:da8:a800:800::8ef]:5173
echo.
pause
