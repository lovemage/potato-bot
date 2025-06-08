# eSIM Telegram Bot 部署指南

## 一、前置準備

### 1. 系統需求
- Python 3.8 或更高版本
- SQLite3
- 穩定的網絡連接
- VPS 或雲服務器（推薦）

### 2. 創建 Telegram Bot
1. 在 Telegram 中搜索 [@BotFather](https://t.me/botfather)
2. 發送 `/newbot` 命令
3. 按照提示設置 bot 名稱和用戶名
4. 保存獲得的 Bot Token

## 二、安裝步驟

### 1. 安裝依賴
```bash
# 創建虛擬環境
python -m venv venv

# 激活虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安裝必要套件
pip install python-telegram-bot sqlite3
```

### 2. 配置文件

創建 `config.py` 文件：

```python
# Bot 配置
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# 數據庫配置
DATABASE_NAME = "esim_store.db"

# 支付配置
PAYMENT_METHODS = {
    "USDT_TRC20": "TXxxxxxxxxxxxxxxxxxxx",
    "PAYPAL": "your-paypal@email.com",
    "ALIPAY": "your-alipay-account"
}

# 管理員 Telegram ID（用於接收訂單通知）
ADMIN_IDS = [123456789]  # 替換為您的 Telegram ID

# 客服鏈接
SUPPORT_USERNAME = "@your_support_username"
```

### 3. 創建啟動腳本

創建 `run.sh`（Linux/Mac）或 `run.bat`（Windows）：

**Linux/Mac (`run.sh`):**
```bash
#!/bin/bash
source venv/bin/activate
python esim_bot.py
```

**Windows (`run.bat`):**
```batch
@echo off
call venv\Scripts\activate
python esim_bot.py
```

## 三、數據庫管理

### 1. 添加新產品

創建 `manage_products.py`：

```python
import sqlite3

def add_product(country, name, data_plan, days, price, inventory, description):
    conn = sqlite3.connect('esim_store.db')
    c = conn.cursor()
    c.execute("""INSERT INTO products 
                 (country, product_name, data_plan, validity_days, price, inventory, description)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (country, name, data_plan, days, price, inventory, description))
    conn.commit()
    conn.close()
    print(f"產品 {name} 已添加")

# 使用示例
if __name__ == "__main__":
    add_product(
        country="台灣",
        name="台灣本地 eSIM 30天",
        data_plan="無限流量",
        days=30,
        price=35.0,
        inventory=200,
        description="台灣三大電信，全島覆蓋，支持5G"
    )
```

### 2. 查看訂單

創建 `view_orders.py`：

```python
import sqlite3
from datetime import datetime

def view_recent_orders(limit=20):
    conn = sqlite3.connect('esim_store.db')
    c = conn.cursor()
    c.execute("""
        SELECT o.id, o.user_id, o.username, p.product_name, 
               o.order_time, o.status
        FROM orders o
        JOIN products p ON o.product_id = p.id
        ORDER BY o.order_time DESC
        LIMIT ?
    """, (limit,))
    
    orders = c.fetchall()
    conn.close()
    
    print(f"最近 {limit} 筆訂單：")
    print("-" * 80)
    for order in orders:
        print(f"訂單ID: {order[0]}")
        print(f"用戶: {order[2]} (ID: {order[1]})")
        print(f"產品: {order[3]}")
        print(f"時間: {order[4]}")
        print(f"狀態: {order[5]}")
        print("-" * 80)

if __name__ == "__main__":
    view_recent_orders()
```

## 四、功能擴展

### 1. 添加管理員功能

在主程序中添加管理員命令：

```python
# 管理員命令
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    
    conn = sqlite3.connect('esim_store.db')
    c = conn.cursor()
    
    # 獲取統計數據
    c.execute("SELECT COUNT(*) FROM orders WHERE date(order_time) = date('now')")
    today_orders = c.fetchone()[0]
    
    c.execute("SELECT SUM(p.price) FROM orders o JOIN products p ON o.product_id = p.id WHERE date(o.order_time) = date('now')")
    today_revenue = c.fetchone()[0] or 0
    
    c.execute("SELECT COUNT(DISTINCT user_id) FROM orders")
    total_customers = c.fetchone()[0]
    
    conn.close()
    
    stats_text = f"""
📊 今日統計

訂單數: {today_orders}
營收: ${today_revenue:.2f}
總客戶數: {total_customers}
    """
    
    await update.message.reply_text(stats_text)

# 在 main() 函數中添加：
application.add_handler(CommandHandler("stats", admin_stats))
```

### 2. 自動發送 eSIM

創建 `esim_delivery.py`：

```python
import qrcode
from io import BytesIO

def generate_esim_qr(activation_code):
    """生成 eSIM QR Code"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    
    # eSIM 激活碼格式
    esim_data = f"LPA:1${activation_code}"
    qr.add_data(esim_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    
    return bio

# 在訂單確認後自動發送
async def send_esim(chat_id, order_id, activation_code):
    # 生成 QR Code
    qr_image = generate_esim_qr(activation_code)
    
    instructions = f"""
📱 您的 eSIM 已準備好！

訂單號: #{order_id}

安裝步驟：
1. 打開手機設置
2. 選擇「行動服務」
3. 點擊「加入 eSIM」
4. 掃描下方 QR Code

激活碼: {activation_code}

注意事項：
- 請在到達目的地後再激活
- 確保手機已解鎖
- 需要網絡連接來下載 eSIM
    """
    
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=qr_image,
        caption=instructions
    )
```

## 五、部署到服務器

### 1. 使用 systemd（Linux）

創建 `/etc/systemd/system/esim-bot.service`：

```ini
[Unit]
Description=eSIM Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot
ExecStart=/path/to/bot/venv/bin/python /path/to/bot/esim_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
sudo systemctl enable esim-bot
sudo systemctl start esim-bot
sudo systemctl status esim-bot
```

### 2. 使用 Docker

創建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "esim_bot.py"]
```

創建 `requirements.txt`：
```
python-telegram-bot==20.3
qrcode==7.4.2
Pillow==10.0.0
```

構建和運行：
```bash
docker build -t esim-bot .
docker run -d --name esim-bot --restart always esim-bot
```

## 六、維護和優化

### 1. 日誌管理

添加日誌輪換：

```python
import logging.handlers

# 設置日誌輪換
handler = logging.handlers.RotatingFileHandler(
    'esim_bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger.addHandler(handler)
```

### 2. 備份數據庫

創建備份腳本 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cp esim_store.db "$BACKUP_DIR/esim_store_$DATE.db"

# 保留最近 7 天的備份
find $BACKUP_DIR -name "esim_store_*.db" -mtime +7 -delete
```

### 3. 監控和告警

創建監控腳本：

```python
import requests
import time

BOT_URL = "https://api.telegram.org/botYOUR_TOKEN/getMe"
CHECK_INTERVAL = 300  # 5 分鐘

def check_bot_status():
    try:
        response = requests.get(BOT_URL)
        if response.status_code == 200:
            print(f"Bot 正常運行: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            send_alert(f"Bot 異常: HTTP {response.status_code}")
    except Exception as e:
        send_alert(f"Bot 無法訪問: {str(e)}")

def send_alert(message):
    # 發送告警到管理員
    # 實現告警邏輯
    pass

if __name__ == "__main__":
    while True:
        check_bot_status()
        time.sleep(CHECK_INTERVAL)
```

## 七、安全建議

1. **Token 安全**
   - 不要將 Token 硬編碼在代碼中
   - 使用環境變量存儲敏感信息

2. **數據庫安全**
   - 定期備份數據庫
   - 限制數據庫文件權限

3. **支付安全**
   - 使用安全的支付網關
   - 記錄所有交易日誌

4. **用戶數據保護**
   - 遵守 GDPR 等隱私法規
   - 加密存儲敏感信息

## 八、常見問題

### Q1: Bot 無響應
- 檢查網絡連接
- 確認 Token 正確
- 查看錯誤日誌

### Q2: 數據庫鎖定
- 確保只有一個進程訪問數據庫
- 使用 WAL 模式提高並發性

### Q3: 內存使用過高
- 實現分頁查詢
- 定期清理過期數據

## 九、聯繫支持

如需技術支持，請聯繫：
- Telegram: @your_support
- Email: support@example.com

---

最後更新: 2024-01-20