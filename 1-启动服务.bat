@echo off
chcp 65001 >nul
title AI 资讯聚合服务 - 运行中

echo ===================================================
echo   正在启动 AI 资讯聚合服务...
echo ===================================================

:: 检查 Python 是否安装
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到 Python，请确保已安装 Python 并添加到环境变量。
    pause
    exit /b 1
)

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 启动服务
echo [INFO] 服务启动中，将在浏览器打开...
timeout /t 2 >nul
start http://127.0.0.1:8000
python app.py

pause
