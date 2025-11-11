@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 启动财务保障应用...

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Python 未安装
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖...
pip install -r requirements.txt

REM 检查数据库文件
if not exist "instance\finance.db" (
    echo 🗄️  初始化数据库...
    python init_db.py
) else (
    echo ✅ 数据库已存在
)

REM 启动应用
echo 🌟 应用启动中...
echo 📱 前端地址: http://localhost:5000
echo 🔌 API地址: http://localhost:5000/api
echo 📝 日志输出:
echo ----------------------------------------

python app.py

pause