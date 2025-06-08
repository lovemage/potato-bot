# 沙發CVV數據庫 Telegram Bot

這是一個專業的卡片銷售 Telegram Bot，支持多種購買方式和完整的錢包系統。

## 功能特色

- 🎯 **裸庫功能**：按國家分類顯示庫存
- 💳 **多種購買方式**：實時卡頭、隨機購買、挑頭、隨機多頭
- 💰 **USDT 錢包系統**：自動充值、扣款、交易記錄
- 📊 **庫存管理**：實時庫存查詢和統計
- 🌍 **多國支持**：美國、日本、韓國、歐洲等多個國家
- 🔒 **安全可靠**：完整的訂單管理和付款確認

## 部署到 Railway

### 1. 準備工作
- 註冊 [Railway](https://railway.app/) 帳號
- 準備您的 Telegram Bot Token

### 2. 部署步驟
1. Fork 或上傳此項目到 GitHub
2. 在 Railway 中創建新項目
3. 連接您的 GitHub 倉庫
4. 設置環境變量（見下方）
5. 部署完成

### 3. 環境變量設置
在 Railway 項目設置中添加以下環境變量：

```
BOT_TOKEN=您的_Telegram_Bot_Token
ADMIN_IDS=管理員_Telegram_ID（用逗號分隔多個）
```

### 4. 文件結構
```
esim-bot/
├── esim-telegram-bot.py    # 主程序
├── config.py               # 配置文件
├── init_db.py             # 數據庫初始化
├── manage_products.py     # 產品管理工具
├── wallet_manager.py      # 錢包管理模組
├── requirements.txt       # Python 依賴
├── Procfile              # Railway 部署配置
├── runtime.txt           # Python 版本
└── README.md             # 說明文件
```

## 本地開發

1. 克隆項目
```bash
git clone <your-repo-url>
cd esim-bot
```

2. 安裝依賴
```bash
pip install -r requirements.txt
```

3. 初始化數據庫
```bash
python init_db.py
```

4. 運行 Bot
```bash
python esim-telegram-bot.py
```

## 管理工具

- `manage_products.py` - 卡片管理工具
- `wallet_admin.py` - 錢包管理工具
- `payment_monitor.py` - 付款監控工具

## 技術棧

- Python 3.11
- python-telegram-bot 20.7
- SQLite 數據庫
- Railway 部署平台

## 支持

如有問題請聯繫管理員或查看項目文檔。 