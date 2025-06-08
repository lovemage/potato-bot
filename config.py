# eSIM Telegram Bot 配置文件

# ==================== 重要：請更新以下配置 ====================

# Bot 基本配置
BOT_TOKEN = "7685096733:AAHw2frruU-kNN_HpLzmx3QjIDqbOPqBxPA"  # ✅ 已設置實際 Bot Token

# 管理員配置
ADMIN_IDS = [7935635650]  # ⚠️ 請替換為您的 Telegram ID，可以添加多個管理員

# 支付配置
PAYMENT_METHODS = {
    "USDT_TRC20": "TXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # ⚠️ 請替換為您的 USDT TRC20 地址
    "PAYPAL": "your-paypal@email.com",  # ⚠️ 請替換為您的 PayPal 郵箱
    "ALIPAY": "your-alipay-account",  # ⚠️ 請替換為您的支付寶帳號
    "STRIPE_PUBLIC_KEY": "pk_test_xxxxxxxxxx",  # Stripe 公鑰
    "STRIPE_SECRET_KEY": "sk_test_xxxxxxxxxx"   # Stripe 私鑰
}

# 客服配置
SUPPORT_USERNAME = "@your_support_username"  # ⚠️ 請替換為您的客服用戶名
SUPPORT_EMAIL = "support@yourdomain.com"     # ⚠️ 請替換為您的客服郵箱

# ==================== 以下配置可保持默認值 ====================

# 數據庫配置
DATABASE_NAME = "esim_store.db"

# API 配置
TRONGRID_API_KEY = "your_trongrid_api_key"  # TronGrid API 密鑰，用於驗證 USDT 交易

# 安全配置
RATE_LIMIT_MAX_CALLS = 10  # 每分鐘最大請求數
RATE_LIMIT_WINDOW = 60     # 速率限制時間窗口（秒）

# 監控配置
ALERT_THRESHOLDS = {
    'response_time': 3.0,  # 響應時間警報閾值（秒）
    'error_rate': 0.1,     # 錯誤率警報閾值（10%）
    'cpu_usage': 80,       # CPU 使用率警報閾值（%）
    'memory_usage': 80     # 內存使用率警報閾值（%）
}

# 備份配置
BACKUP_INTERVAL_HOURS = 24  # 自動備份間隔（小時）
BACKUP_KEEP_COUNT = 7       # 保留備份文件數量

# 日誌配置
LOG_LEVEL = "INFO"
LOG_FILE = "esim_bot.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 多語言支持
DEFAULT_LANGUAGE = "zh"
SUPPORTED_LANGUAGES = ["zh", "en", "ja", "ko"]

# 產品配置
LOW_STOCK_THRESHOLD = 10  # 低庫存警報閾值
AUTO_RESTOCK_ENABLED = True

# 通知配置
NOTIFICATION_CHANNELS = {
    "new_order": True,
    "payment_received": True,
    "low_stock": True,
    "system_alerts": True
} 