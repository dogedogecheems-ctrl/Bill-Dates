#!/bin/bash

# 财务保障应用启动脚本

echo "🚀 启动财务保障应用..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 检查数据库文件
if [ ! -f "instance/finance.db" ]; then
    echo "🗄️  初始化数据库..."
    Python init_db.py
else
    echo "✅ 数据库已存在"
fi

# 启动应用
echo "🌟 应用启动中..."
echo "📱 前端地址: http://localhost:5000"
echo "🔌 API地址: http://localhost:5000/api"
echo "📝 日志输出:"
echo "----------------------------------------"

Python app.py