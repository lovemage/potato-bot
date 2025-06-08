# payment_handler.py - 支付處理模組

import hashlib
import hmac
import json
import aiohttp
from datetime import datetime
import asyncio
from typing import Dict, Optional

class PaymentHandler:
    """處理各種支付方式的整合"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.payment_methods = {
            'usdt_trc20': self.handle_usdt_payment,
            'paypal': self.handle_paypal_payment,
            'stripe': self.handle_stripe_payment,
            'alipay': self.handle_alipay_payment
        }
    
    async def process_payment(self, order_id: int, amount: float, method: str) -> Dict:
        """處理支付請求"""
        if method not in self.payment_methods:
            return {'success': False, 'error': 'Unsupported payment method'}
        
        handler = self.payment_methods[method]
        return await handler(order_id, amount)
    
    async def handle_usdt_payment(self, order_id: int, amount: float) -> Dict:
        """處理 USDT 支付"""
        # 生成唯一支付地址或帶 memo 的地址
        payment_address = self.config['USDT_ADDRESS']
        memo = f"ORDER{order_id}"
        
        return {
            'success': True,
            'payment_info': {
                'address': payment_address,
                'amount': amount,
                'memo': memo,
                'network': 'TRC20',
                'timeout': 3600  # 1小時超時
            }
        }
    
    async def verify_usdt_transaction(self, tx_hash: str, expected_amount: float) -> bool:
        """驗證 USDT 交易"""
        # 這裡需要接入 TronGrid API 或類似服務
        api_key = self.config.get('TRONGRID_API_KEY')
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.trongrid.io/v1/transactions/{tx_hash}"
            headers = {'TRON-PRO-API-KEY': api_key}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # 解析交易數據，驗證金額和接收地址
                    # 這裡需要根據實際 API 響應格式調整
                    return self._validate_transaction(data, expected_amount)
        
        return False
    
    def _validate_transaction(self, tx_data: Dict, expected_amount: float) -> bool:
        """驗證交易詳情"""
        # 實現交易驗證邏輯
        # 檢查：接收地址、金額、確認數等
        pass
    
    async def handle_paypal_payment(self, order_id: int, amount: float) -> Dict:
        """處理 PayPal 支付"""
        # PayPal API 集成
        pass
    
    async def handle_stripe_payment(self, order_id: int, amount: float) -> Dict:
        """處理 Stripe 支付"""
        # Stripe API 集成
        pass
    
    async def handle_alipay_payment(self, order_id: int, amount: float) -> Dict:
        """處理支付寶支付"""
        # 支付寶 API 集成
        pass

# advanced_features.py - 進階功能模組

import schedule
import time
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

class AdvancedFeatures:
    """Bot 進階功能"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def generate_sales_report(self, period: str = 'daily') -> BytesIO:
        """生成銷售報表"""
        conn = sqlite3.connect(self.db_path)
        
        # 根據期間獲取數據
        if period == 'daily':
            query = """
                SELECT DATE(order_time) as date, COUNT(*) as orders, 
                       SUM(p.price) as revenue
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE order_time >= datetime('now', '-7 days')
                GROUP BY DATE(order_time)
                ORDER BY date
            """
        elif period == 'monthly':
            query = """
                SELECT strftime('%Y-%m', order_time) as month, 
                       COUNT(*) as orders, SUM(p.price) as revenue
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE order_time >= datetime('now', '-6 months')
                GROUP BY strftime('%Y-%m', order_time)
                ORDER BY month
            """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # 創建圖表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # 訂單數量圖
        ax1.plot(df.iloc[:, 0], df['orders'], marker='o')
        ax1.set_title('訂單數量趨勢')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('訂單數')
        ax1.grid(True)
        
        # 營收圖
        ax2.bar(df.iloc[:, 0], df['revenue'])
        ax2.set_title('營收趨勢')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('營收 (USD)')
        ax2.grid(True, axis='y')
        
        plt.tight_layout()
        
        # 保存到內存
        bio = BytesIO()
        plt.savefig(bio, format='png')
        bio.seek(0)
        plt.close()
        
        return bio
    
    async def auto_restock_notification(self, threshold: int = 10):
        """低庫存自動通知"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT product_name, inventory 
            FROM products 
            WHERE inventory < ?
        """, (threshold,))
        
        low_stock_items = c.fetchall()
        conn.close()
        
        if low_stock_items:
            message = "⚠️ 低庫存警告:\n\n"
            for item, stock in low_stock_items:
                message += f"📦 {item}: 剩餘 {stock} 個\n"
            
            return message
        
        return None
    
    async def customer_analytics(self, user_id: int) -> Dict:
        """客戶分析"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 獲取客戶統計
        c.execute("""
            SELECT COUNT(*) as total_orders,
                   SUM(p.price) as total_spent,
                   AVG(p.price) as avg_order_value,
                   MAX(o.order_time) as last_order
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = ?
        """, (user_id,))
        
        stats = c.fetchone()
        
        # 獲取最常購買的產品
        c.execute("""
            SELECT p.country, COUNT(*) as purchase_count
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = ?
            GROUP BY p.country
            ORDER BY purchase_count DESC
            LIMIT 3
        """, (user_id,))
        
        favorite_destinations = c.fetchall()
        conn.close()
        
        return {
            'total_orders': stats[0] or 0,
            'total_spent': stats[1] or 0,
            'avg_order_value': stats[2] or 0,
            'last_order': stats[3],
            'favorite_destinations': favorite_destinations
        }
    
    async def promotional_campaigns(self):
        """促銷活動管理"""
        campaigns = {
            'new_user': {
                'discount': 0.2,  # 20% 折扣
                'condition': lambda user: user.order_count == 0,
                'message': '🎉 新用戶專享 20% 折扣！'
            },
            'bulk_purchase': {
                'discount': 0.15,  # 15% 折扣
                'condition': lambda cart: len(cart) >= 3,
                'message': '🛒 購買3個以上享 15% 折扣！'
            },
            'weekend_special': {
                'discount': 0.1,  # 10% 折扣
                'condition': lambda: datetime.now().weekday() in [5, 6],
                'message': '🌟 週末特惠 10% 折扣！'
            }
        }
        
        return campaigns

# notification_service.py - 通知服務

class NotificationService:
    """處理各種通知"""
    
    def __init__(self, bot, admin_ids: list):
        self.bot = bot
        self.admin_ids = admin_ids
    
    async def notify_new_order(self, order_details: Dict):
        """通知管理員新訂單"""
        message = f"""
🔔 新訂單通知

訂單號: #{order_details['order_id']}
客戶: {order_details['username']} ({order_details['user_id']})
產品: {order_details['product_name']}
金額: ${order_details['amount']}
時間: {order_details['time']}
        """
        
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(chat_id=admin_id, text=message)
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")
    
    async def notify_payment_received(self, payment_details: Dict):
        """通知支付已收到"""
        message = f"""
💰 支付確認

訂單號: #{payment_details['order_id']}
支付方式: {payment_details['method']}
金額: ${payment_details['amount']}
交易ID: {payment_details['transaction_id']}
        """
        
        # 通知客戶
        await self.bot.send_message(
            chat_id=payment_details['user_id'],
            text="✅ 支付已確認！正在處理您的訂單..."
        )
        
        # 通知管理員
        for admin_id in self.admin_ids:
            await self.bot.send_message(chat_id=admin_id, text=message)
    
    async def send_esim_delivery(self, user_id: int, esim_data: Dict):
        """發送 eSIM 交付信息"""
        # 生成安裝指南圖片
        instructions_image = self._generate_instructions_image(esim_data)
        
        message = f"""
📱 您的 eSIM 已準備就緒！

📍 適用地區: {esim_data['country']}
📊 數據方案: {esim_data['data_plan']}
📅 有效期: {esim_data['validity_days']}天

激活碼: {esim_data['activation_code']}

請按照以下步驟安裝：
1️⃣ 確保已連接 WiFi
2️⃣ 打開設置 > 行動服務
3️⃣ 選擇"加入 eSIM"
4️⃣ 掃描 QR Code 或手動輸入激活碼

⚠️ 注意事項：
• 請在到達目的地後激活
• 一旦激活無法轉移到其他設備
• 如需協助請聯繫客服
        """
        
        # 發送 QR Code
        qr_code = self._generate_esim_qr(esim_data['activation_code'])
        await self.bot.send_photo(
            chat_id=user_id,
            photo=qr_code,
            caption=message
        )
        
        # 發送安裝指南
        if instructions_image:
            await self.bot.send_photo(
                chat_id=user_id,
                photo=instructions_image,
                caption="📖 詳細安裝指南"
            )
    
    def _generate_esim_qr(self, activation_code: str) -> BytesIO:
        """生成 eSIM QR Code"""
        import qrcode
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # eSIM 標準格式
        qr_data = f"LPA:1${activation_code}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        bio = BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        
        return bio
    
    def _generate_instructions_image(self, esim_data: Dict) -> Optional[BytesIO]:
        """生成安裝指南圖片"""
        # 這裡可以根據不同手機型號生成對應的安裝指南
        # 返回 None 或圖片的 BytesIO 對象
        return None

# multi_language_support.py - 多語言支持

class MultiLanguageSupport:
    """多語言支持模組"""
    
    def __init__(self):
        self.translations = {
            'en': {
                'welcome': 'Welcome to eSIM Store!',
                'select_country': 'Please select a country:',
                'no_stock': 'Sorry, no stock available',
                'confirm_purchase': 'Confirm Purchase',
                'payment_success': 'Payment successful!',
                'help': 'Help',
                'support': 'Support',
                'my_orders': 'My Orders'
            },
            'zh_TW': {
                'welcome': '歡迎來到 eSIM 商店！',
                'select_country': '請選擇國家：',
                'no_stock': '抱歉，暫無庫存',
                'confirm_purchase': '確認購買',
                'payment_success': '支付成功！',
                'help': '使用說明',
                'support': '客服支持',
                'my_orders': '我的訂單'
            },
            'zh_CN': {
                'welcome': '欢迎来到 eSIM 商店！',
                'select_country': '请选择国家：',
                'no_stock': '抱歉，暂无库存',
                'confirm_purchase': '确认购买',
                'payment_success': '支付成功！',
                'help': '使用说明',
                'support': '客服支持',
                'my_orders': '我的订单'
            }
        }
        
        self.user_languages = {}  # 存儲用戶語言偏好
    
    def get_text(self, user_id: int, key: str) -> str:
        """獲取用戶語言的文本"""
        lang = self.user_languages.get(user_id, 'zh_TW')
        return self.translations.get(lang, {}).get(key, key)
    
    def set_user_language(self, user_id: int, language: str):
        """設置用戶語言"""
        if language in self.translations:
            self.user_languages[user_id] = language
    
    def get_language_keyboard(self):
        """獲取語言選擇鍵盤"""
        keyboard = []
        for lang_code, lang_name in [('en', 'English'), ('zh_TW', '繁體中文'), ('zh_CN', '简体中文')]:
            keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
        return InlineKeyboardMarkup(keyboard)