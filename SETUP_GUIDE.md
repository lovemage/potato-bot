# 🚀 卡片 Telegram Bot 設定指南

## 📋 快速開始

### 1. 建立資料庫

```bash
# 初始化資料庫（包含 25 張示例卡片）
python3 init_db.py
```

### 2. 設定 Telegram Bot

#### 步驟 1：創建 Bot
1. 在 Telegram 中搜索 `@BotFather`
2. 發送 `/newbot` 命令
3. 設置 Bot 名稱（例如：`My Card Store Bot`）
4. 設置 Bot 用戶名（例如：`my_card_store_bot`）
5. **保存獲得的 Bot Token**

#### 步驟 2：獲取您的 Telegram ID
1. 在 Telegram 中搜索 `@userinfobot`
2. 發送 `/start` 命令
3. **記下您的 User ID（數字）**

#### 步驟 3：更新配置文件
編輯 `config.py` 文件，更新以下重要配置：

```python
# Bot Token（必須更新）
BOT_TOKEN = "您的_實際_Bot_Token"

# 管理員 ID（必須更新）
ADMIN_IDS = [您的_實際_Telegram_ID]

# 支付方式（建議更新）
PAYMENT_METHODS = {
    "USDT_TRC20": "您的_USDT_地址",
    "PAYPAL": "您的_PayPal_郵箱",
    "ALIPAY": "您的_支付寶帳號"
}

# 客服信息（建議更新）
SUPPORT_USERNAME = "@您的_客服用戶名"
SUPPORT_EMAIL = "您的_客服郵箱"
```

### 3. 啟動 Bot

```bash
# 方法 1：使用啟動腳本
./run.sh

# 方法 2：直接運行
python3 esim-telegram-bot.py
```

## 🛠️ 管理工具

### 卡片管理

```bash
# 查看所有卡片
python3 manage_products.py list

# 查看特定國家的卡片
python3 manage_products.py list "UNITED STATES"

# 添加新卡片
python3 manage_products.py add

# 批量導入卡片
python3 manage_products.py import

# 更新卡片價格
python3 manage_products.py price 1 25.99

# 更新卡片狀態
python3 manage_products.py status 1 sold

# 刪除卡片
python3 manage_products.py delete 1
```

### 訂單管理

```bash
# 查看訂單
python3 view_orders.py
```

### 系統測試

```bash
# 運行系統測試
python3 test_setup.py
```

## 📝 卡片格式

支持的卡片格式：`號碼|日期|密鑰|國家`

示例：
```
371500837215003|04/29|6418|UNITED STATES
379382534811000|07/26|9097|UNITED STATES
378282246310005|03/28|1234|JAPAN
```

### 批量導入卡片

1. 準備卡片數據文件（每行一張卡片）
2. 運行導入命令：
```bash
python3 manage_products.py import
```
3. 選擇文件或直接粘貼數據

## 🔧 配置說明

### 必須更新的配置

| 配置項 | 說明 | 示例 |
|--------|------|------|
| `BOT_TOKEN` | Telegram Bot Token | `123456:ABC-DEF...` |
| `ADMIN_IDS` | 管理員 Telegram ID | `[123456789]` |

### 建議更新的配置

| 配置項 | 說明 | 示例 |
|--------|------|------|
| `USDT_TRC20` | USDT 收款地址 | `TXxxxxx...` |
| `PAYPAL` | PayPal 郵箱 | `pay@example.com` |
| `SUPPORT_USERNAME` | 客服用戶名 | `@support` |

## 🚨 故障排除

### 常見問題

1. **Bot 無響應**
   - 檢查 Bot Token 是否正確
   - 確認網絡連接正常
   - 查看錯誤日誌

2. **資料庫錯誤**
   - 重新初始化資料庫：`python3 init_db.py`
   - 檢查文件權限

3. **卡片導入失敗**
   - 檢查格式是否正確：`號碼|日期|密鑰|國家`
   - 確認卡號不重複

### 日誌查看

```bash
# 查看實時日誌
tail -f esim_bot.log

# 查看錯誤日誌
grep ERROR esim_bot.log
```

## 📊 功能特色

- ✅ 支持多國卡片銷售
- ✅ 自動訂單管理
- ✅ 多種支付方式
- ✅ 管理員後台功能
- ✅ 安全監控
- ✅ 自動備份
- ✅ 詳細日誌記錄

## 🔐 安全建議

1. **保護敏感信息**
   - 不要將 Bot Token 公開
   - 定期更換支付地址
   - 限制管理員權限

2. **定期備份**
   - 自動備份已啟用
   - 手動備份重要數據

3. **監控系統**
   - 查看系統日誌
   - 監控異常活動

## 📞 技術支持

如需幫助，請：
1. 查看此設定指南
2. 運行系統測試：`python3 test_setup.py`
3. 查看日誌文件
4. 聯繫技術支持

---

**最後更新：2025-06-08** 