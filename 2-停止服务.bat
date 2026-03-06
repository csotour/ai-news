@echo off
chcp 65001 >nul
title 关闭 AI 资讯聚合服务

echo ===================================================
echo   正在关闭 AI 资讯聚合服务...
echo ===================================================

:: 查找并结束使用 8000 端口的 Python 进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    if "%%a" neq "0" (
        echo [INFO] 找到运行在端口 8000 的进程 PID: %%a
        taskkill /F /PID %%a >nul 2>&1
        echo [SUCCESS] 服务已成功关闭！
        goto end
    )
)

echo [INFO] 未发现运行中的服务。

:end
timeout /t 2 >nul
