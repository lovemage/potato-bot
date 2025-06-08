#!/bin/bash

# eSIM Telegram Bot 啟動腳本

echo "🚀 正在啟動 eSIM Telegram Bot..."

# 檢查 Python 版本
python_version=$(python3 --version 2>&1)
echo "Python 版本: $python_version"

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# 激活虛擬環境
echo "🔧 激活虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo "📥 安裝依賴包..."
pip install --upgrade pip
pip install -r requirements.txt

# 檢查配置文件
if [ ! -f "config.py" ]; then
    echo "❌ 錯誤: 找不到 config.py 文件"
    echo "請先配置您的 Bot Token 和其他設置"
    exit 1
fi

# 檢查 Bot Token
if grep -q "YOUR_BOT_TOKEN_HERE" config.py; then
    echo "❌ 錯誤: 請在 config.py 中設置您的 Bot Token"
    echo "編輯 config.py 文件，將 YOUR_BOT_TOKEN_HERE 替換為您的實際 Token"
    exit 1
fi

# 創建必要的目錄
mkdir -p logs
mkdir -p backups

# 啟動 Bot
echo "✅ 配置檢查完成，正在啟動 Bot..."
python3 esim-telegram-bot.py 