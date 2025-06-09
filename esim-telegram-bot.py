import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json
from datetime import datetime
import config
from wallet_manager import wallet_manager

# 設置日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 數據庫設置
def init_db():
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 創建產品表
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  country TEXT NOT NULL,
                  product_name TEXT NOT NULL,
                  data_plan TEXT NOT NULL,
                  validity_days INTEGER NOT NULL,
                  price REAL NOT NULL,
                  inventory INTEGER NOT NULL,
                  description TEXT)''')
    
    # 創建訂單表
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  username TEXT,
                  product_id INTEGER NOT NULL,
                  order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  status TEXT DEFAULT 'pending',
                  FOREIGN KEY (product_id) REFERENCES products (id))''')
    
    # 插入示例數據
    sample_products = [
        # 亞洲地區
        ('日本', '日本高速 eSIM 7天', '每日2GB高速', 7, 25.0, 100, '覆蓋日本全境，支持4G/5G網絡'),
        ('日本', '日本無限流量 eSIM 30天', '無限流量', 30, 88.0, 50, '真正無限流量，不限速'),
        ('韓國', '韓國旅遊 eSIM 5天', '每日1GB', 5, 18.0, 80, '覆蓋首爾、釜山等主要城市'),
        ('韓國', '韓國商務 eSIM 15天', '總計20GB', 15, 45.0, 60, '高速穩定，適合商務使用'),
        ('泰國', '泰國度假 eSIM 10天', '總計15GB', 10, 22.0, 120, '支持泰國所有電信運營商'),
        ('新加坡', '新加坡城市 eSIM 3天', '每日3GB', 3, 15.0, 90, '新加坡全島覆蓋'),
        
        # 歐洲地區
        ('歐洲', '歐洲多國 eSIM 15天', '總計10GB', 15, 35.0, 70, '覆蓋30+歐洲國家'),
        ('歐洲', '歐洲無限 eSIM 30天', '無限流量', 30, 99.0, 40, '歐盟全境通用'),
        ('英國', '英國倫敦 eSIM 7天', '每日2GB', 7, 28.0, 55, '英國全境4G/5G網絡'),
        ('法國', '法國巴黎 eSIM 5天', '總計8GB', 5, 20.0, 65, '法國電信官方合作'),
        
        # 美洲地區
        ('美國', '美國全境 eSIM 14天', '無限流量', 14, 58.0, 85, 'AT&T/T-Mobile網絡'),
        ('美國', '美國西岸 eSIM 7天', '每日3GB', 7, 32.0, 95, '洛杉磯、舊金山等地'),
        ('加拿大', '加拿大 eSIM 10天', '總計15GB', 10, 42.0, 45, '多倫多、溫哥華等主要城市'),
        
        # 其他地區
        ('澳洲', '澳洲旅遊 eSIM 14天', '總計20GB', 14, 48.0, 60, '雪梨、墨爾本全覆蓋'),
        ('全球', '全球通用 eSIM 30天', '總計5GB', 30, 89.0, 30, '覆蓋100+國家地區')
    ]
    
    # 檢查是否已有數據
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        c.executemany('''INSERT INTO products 
                        (country, product_name, data_plan, validity_days, price, inventory, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''', sample_products)
    
    conn.commit()
    conn.close()

# 獲取所有國家/地區 - 更新為讀取cards和full_data表
def get_countries():
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 從兩個表中獲取所有可用的國家
    c.execute("""
        SELECT DISTINCT country FROM cards WHERE status = 'available'
        UNION
        SELECT DISTINCT country FROM full_data WHERE status = 'available'
        ORDER BY country
    """)
    countries = [row[0] for row in c.fetchall()]
    conn.close()
    return countries

# 獲取特定國家的卡片 - 更新為讀取cards和full_data表
def get_cards_by_country(country):
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 從裸庫表獲取卡片
    c.execute("""SELECT id, card_number, expiry_date, security_code, price, 'naked' as type
                 FROM cards 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY price""", (country,))
    naked_cards = c.fetchall()
    
    # 從全資料表獲取卡片
    c.execute("""SELECT id, card_number, expiry_date, security_code, price, 'full' as type
                 FROM full_data 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY price""", (country,))
    full_cards = c.fetchall()
    
    # 合併結果
    all_cards = naked_cards + full_cards
    conn.close()
    return all_cards

# 獲取卡片詳情 - 更新為支持兩個表
def get_card_details(card_id, card_type='naked'):
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    if card_type == 'full':
        c.execute("""SELECT * FROM full_data WHERE id = ?""", (card_id,))
    else:
        c.execute("""SELECT * FROM cards WHERE id = ?""", (card_id,))
    
    card = c.fetchone()
    conn.close()
    return card

# 創建訂單 - 更新為支持兩個表
def create_order(user_id, username, card_id, card_type='naked'):
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 選擇正確的表
    table_name = 'full_data' if card_type == 'full' else 'cards'
    
    # 檢查卡片狀態
    c.execute(f"SELECT status FROM {table_name} WHERE id = ?", (card_id,))
    result = c.fetchone()
    
    if result and result[0] == 'available':
        # 創建訂單 - 需要先確保orders表存在並適配新結構
        try:
            c.execute("""INSERT INTO orders (user_id, username, card_id, card_type, order_time, status) 
                         VALUES (?, ?, ?, ?, datetime('now'), 'pending')""", 
                     (user_id, username, card_id, card_type))
        except sqlite3.OperationalError:
            # 如果orders表結構不匹配，創建新的orders表
            c.execute('''CREATE TABLE IF NOT EXISTS orders_new
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          username TEXT,
                          card_id INTEGER NOT NULL,
                          card_type TEXT DEFAULT 'naked',
                          order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          status TEXT DEFAULT 'pending')''')
            c.execute("""INSERT INTO orders_new (user_id, username, card_id, card_type, order_time, status) 
                         VALUES (?, ?, ?, ?, datetime('now'), 'pending')""", 
                     (user_id, username, card_id, card_type))
        
        # 標記卡片為已售出
        c.execute(f"UPDATE {table_name} SET status = 'sold' WHERE id = ?", (card_id,))
        
        conn.commit()
        order_id = c.lastrowid
        conn.close()
        return order_id
    else:
        conn.close()
        return None

# 獲取用戶訂單 - 更新為支持新的訂單結構
def get_user_orders(user_id):
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    try:
        # 嘗試使用新的orders表結構
        c.execute("""
            SELECT o.id, o.card_id, o.card_type, o.order_time, o.status
            FROM orders_new o
            WHERE o.user_id = ?
            ORDER BY o.order_time DESC
            LIMIT 10
        """, (user_id,))
        orders = c.fetchall()
    except sqlite3.OperationalError:
        # 如果新表不存在，返回空列表
        orders = []
    
    conn.close()
    return orders

# 自動刪除上一個訊息的功能
async def delete_previous_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.warning(f"無法刪除訊息 {message_id}: {e}")

# 更新訊息ID的輔助函數
def update_last_message_id(context: ContextTypes.DEFAULT_TYPE, message_id: int):
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    context.chat_data['user_data']['last_message_id'] = message_id

# 安全編輯訊息的輔助函數
async def safe_edit_message(query, text, reply_markup=None):
    try:
        logger.info(f"嘗試編輯訊息: {text[:50]}...")
        return await query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"編輯訊息失敗: {e}")
        # 如果編輯失敗（通常是因為原訊息包含圖片），則刪除原訊息並發送新訊息
        try:
            await query.message.delete()
            logger.info("已刪除原訊息")
        except Exception as delete_error:
            logger.warning(f"刪除原訊息失敗: {delete_error}")
        
        try:
            logger.info("嘗試發送新訊息")
            return await query.message.reply_text(text, reply_markup=reply_markup)
        except Exception as reply_error:
            logger.error(f"發送新訊息失敗: {reply_error}")
            # 最後嘗試直接發送到聊天
            return await query.message.chat.send_message(text, reply_markup=reply_markup)

# 命令處理器
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # 刪除用戶的命令訊息
    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"無法刪除用戶命令訊息: {e}")
    
    welcome_text = f"""🌐 歡迎使用【全球 沙發CVV數據庫】

您好！{user.first_name} 我是您的數據專屬助理馬鈴薯 🤖

我們堅持一手/二手/品質第一/堅若磐石

🇯🇵 日本 | 🇰🇷 韓國 | 🇹🇭 泰國

🇸🇬 新加坡 | 🇺🇸 美國 | 🇪🇺 歐洲

🇦🇺 澳洲 | 🇬🇧 英國 | 🇨🇳 中國

如何開始？

點擊下方按鈕，立即探索適合您的 數據 方案！"""
    
    # 創建自定義鍵盤
    keyboard = [
        # 第一行：三個愛心按鈕
        [
            InlineKeyboardButton("裸庫❤️", callback_data="naked_stock"),
            InlineKeyboardButton("特價❤️", callback_data="special_price"),
            InlineKeyboardButton("全資❤️", callback_data="full_fund")
        ],
        # 第二行：語言和信息按鈕
        [
            InlineKeyboardButton("English", callback_data="english"),
            InlineKeyboardButton("中文", callback_data="chinese"),
            InlineKeyboardButton("售價信息", callback_data="price_info"),
            InlineKeyboardButton("賬戶充值", callback_data="account_recharge")
        ],
        # 第三行：主要功能按鈕
        [
            InlineKeyboardButton("選頭購買", callback_data="browse"),
            InlineKeyboardButton("庫存卡頭查詢", callback_data="stock_query"),
            InlineKeyboardButton("訂單記錄", callback_data="my_orders"),
            InlineKeyboardButton("卡頭收藏", callback_data="card_favorites")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 發送歡迎圖片和文字
    try:
        with open('image.png', 'rb') as photo:
            message = await update.effective_chat.send_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        # 如果圖片文件不存在，則只發送文字
        logger.warning("image.png 文件未找到，僅發送文字訊息")
        message = await update.effective_chat.send_message(welcome_text, reply_markup)
    except Exception as e:
        # 如果發送圖片失敗，則發送文字
        logger.error(f"發送圖片失敗: {e}，改為發送文字訊息")
        message = await update.effective_chat.send_message(welcome_text, reply_markup)
    
    # 保存當前訊息ID到用戶上下文中
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    context.chat_data['user_data']['last_message_id'] = message.message_id

# 瀏覽卡片
async def browse_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    countries = get_countries()
    
    if not countries:
        await safe_edit_message(query, "暫無可用卡片")
        return
    
    keyboard = []
    # 每行顯示2個國家
    for i in range(0, len(countries), 2):
        row = []
        row.append(InlineKeyboardButton(f"🌍 {countries[i]}", callback_data=f"country_{countries[i]}"))
        if i + 1 < len(countries):
            row.append(InlineKeyboardButton(f"🌍 {countries[i+1]}", callback_data=f"country_{countries[i+1]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = await safe_edit_message(query, "請選擇地區：", reply_markup)
    update_last_message_id(context, message.message_id)

# 顯示國家卡片
async def show_country_cards(update: Update, context: ContextTypes.DEFAULT_TYPE, country: str):
    query = update.callback_query
    
    cards = get_cards_by_country(country)
    
    if not cards:
        keyboard = [[InlineKeyboardButton("🔙 返回地區選擇", callback_data="browse")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, f"抱歉，{country} 暫無可用卡片", reply_markup)
        return
    
    text = f"🌍 {country} 可用卡片：\n\n"
    
    for card in cards:
        card_id, card_number, expiry_date, security_code, price = card
        # 隱藏部分卡號信息
        masked_number = card_number[:4] + "*" * 8 + card_number[-4:]
        text += f"💳 卡號: {masked_number}\n"
        text += f"📅 到期: {expiry_date}\n"
        text += f"💰 價格: ${price}\n"
        text += "➖➖➖➖➖➖➖➖➖\n"
    
    keyboard = []
    for card in cards:
        card_id, card_number, expiry_date, security_code, price = card
        masked_number = card_number[:4] + "*" * 8 + card_number[-4:]
        keyboard.append([InlineKeyboardButton(
            f"🛒 購買 {masked_number} - ${price}", 
            callback_data=f"buy_{card_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 返回地區選擇", callback_data="browse")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 處理購買
async def handle_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, card_id: int):
    query = update.callback_query
    
    user = update.effective_user
    card = get_card_details(card_id)
    
    if not card:
        await safe_edit_message(query, "卡片不存在")
        return
    
    _, card_number, expiry_date, security_code, country, price, status, created_time = card
    
    if status != 'available':
        await safe_edit_message(query, "抱歉，該卡片已售出")
        return
    
    # 隱藏部分卡號信息
    masked_number = card_number[:4] + "*" * 8 + card_number[-4:]
    
    text = f"""
💳 確認購買

卡號: {masked_number}
到期日: {expiry_date}
國家: {country}
價格: ${price}

請確認購買？
    """
    
    keyboard = [
        [
            InlineKeyboardButton("✅ 確認購買", callback_data=f"confirm_{card_id}"),
            InlineKeyboardButton("❌ 取消", callback_data=f"country_{country}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 確認購買
async def confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, card_id: int):
    query = update.callback_query
    
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # 獲取卡片詳情
    card = get_card_details(card_id)
    if not card:
        await safe_edit_message(query, "❌ 卡片不存在或已售出")
        return
    
    card_id, card_number, expiry_date, security_code, country, price, status, created_time = card
    
    if status != 'available':
        await safe_edit_message(query, "❌ 卡片已售出")
        return
    
    # 檢查用戶餘額
    wallet_manager.get_or_create_wallet(user_id, username)
    current_balance = wallet_manager.get_balance(user_id)
    
    if current_balance >= price:
        # 餘額充足，直接扣款購買
        success, new_balance, message = wallet_manager.deduct_balance(
            user_id, username, price, f"購買卡片 {card_number[:4]}****{card_number[-4:]}"
        )
        
        if success:
            # 創建訂單並標記為已完成
            order_id = create_order(user_id, username, card_id)
            
            if order_id:
                # 更新訂單狀態為已完成
                conn = sqlite3.connect(config.DATABASE_NAME)
                c = conn.cursor()
                c.execute("UPDATE orders SET status = 'completed' WHERE id = ?", (order_id,))
                conn.commit()
                conn.close()
                
                text = f"""
✅ 購買成功！

📋 卡片詳情：
卡號: {card_number}
到期: {expiry_date}
密鑰: {security_code}
國家: {country}

💰 付款信息：
扣款金額: ${price} USDT
餘額: ${new_balance:.2f} USDT

請妥善保存卡片信息
                """
                
                keyboard = [
                    [InlineKeyboardButton("💳 查看餘額", callback_data="check_balance")],
                    [InlineKeyboardButton("🛒 繼續購買", callback_data="browse")],
                    [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
                ]
                
                # 通知管理員
                admin_text = f"""
✅ 自動購買成功

用戶: {username} (ID: {user_id})
卡片: {card_number}
國家: {country}
金額: ${price} USDT
餘額: ${new_balance:.2f} USDT
訂單ID: {order_id}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                for admin_id in config.ADMIN_IDS:
                    try:
                        await context.bot.send_message(chat_id=admin_id, text=admin_text)
                    except Exception as e:
                        logger.error(f"無法通知管理員 {admin_id}: {e}")
            else:
                text = "❌ 訂單創建失敗，請聯繫客服"
                keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        else:
            text = f"❌ 扣款失敗: {message}"
            keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    else:
        # 餘額不足，提供充值選項
        shortage = price - current_balance
        text = f"""
⚠️ 餘額不足

當前餘額: ${current_balance:.2f} USDT
卡片價格: ${price:.2f} USDT
還需充值: ${shortage:.2f} USDT

請先充值後再購買
        """
        
        keyboard = [
            [InlineKeyboardButton("💰 立即充值", callback_data="account_recharge")],
            [InlineKeyboardButton("💳 查看餘額", callback_data="check_balance")],
            [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 處理付款憑證上傳
async def handle_payment_upload(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: int):
    query = update.callback_query
    
    text = f"""
📤 付款憑證上傳

訂單號: #{order_id}

請發送您的付款截圖或憑證。
支持的格式：圖片、PDF

發送後我們將盡快為您確認訂單。
    """
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 回調查詢處理器
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    logger.info(f"處理按鈕回調: {data}")
    
    # 清除任何等待狀態（除非是充值相關按鈕）
    if not data.startswith("account_recharge") and not data.startswith("check_balance"):
        context.user_data.pop('waiting_for_recharge_amount', None)
    
    # 首先回應查詢，避免超時
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"回應查詢時出錯: {e}")
    
    # 自動刪除上一個訊息（保持視窗乾淨）
    try:
        if 'user_data' in context.chat_data and 'last_message_id' in context.chat_data['user_data']:
            last_message_id = context.chat_data['user_data']['last_message_id']
            if last_message_id != query.message.message_id:
                await delete_previous_message(context, query.message.chat_id, last_message_id)
    except Exception as e:
        logger.warning(f"刪除上一個訊息時出錯: {e}")
    
    # 添加總體錯誤處理
    try:
        if data == "browse":
            await browse_cards(update, context)
        elif data == "main_menu":
            await show_main_menu(update, context)
        elif data.startswith("country_"):
            country = data.replace("country_", "")
            await show_country_cards(update, context, country)
        elif data.startswith("buy_"):
            card_id = int(data.replace("buy_", ""))
            await handle_purchase(update, context, card_id)
        elif data.startswith("confirm_"):
            card_id = int(data.replace("confirm_", ""))
            await confirm_purchase(update, context, card_id)
        elif data.startswith("payment_"):
            order_id = int(data.replace("payment_", ""))
            await handle_payment_upload(update, context, order_id)
        elif data == "help":
            await show_help(update, context)
        elif data == "support":
            await show_support(update, context)
        elif data == "my_orders":
            await show_my_orders(update, context)
        # 新增的按鈕處理
        elif data == "naked_stock":
            await show_naked_stock(update, context)
        elif data.startswith("naked_country_"):
            await show_naked_country_details(update, context)
        elif data.startswith("buy_card_"):
            card_id = int(data.replace("buy_card_", ""))
            await handle_purchase(update, context, card_id)
        elif data.startswith("buy_full_"):
            card_id = int(data.replace("buy_full_", ""))
            await handle_full_purchase(update, context, card_id)
        elif data.startswith("confirm_full_"):
            card_id = int(data.replace("confirm_full_", ""))
            await confirm_full_purchase(update, context, card_id)
        elif data.startswith("realtime_"):
            await show_realtime_cards(update, context)
        elif data.startswith("random_buy_") or data.startswith("random_"):
            await handle_random_purchase(update, context)
        elif data.startswith("pick_card_"):
            await show_pick_cards(update, context)
        elif data.startswith("confirm_random_"):
            card_ids = data.replace("confirm_random_", "").split(",")
            # 處理多卡片購買確認
            await handle_multiple_purchase(update, context, card_ids)
        elif data == "special_price":
            await show_special_price(update, context)
        elif data == "full_fund":
            await show_full_fund(update, context)
        elif data.startswith("full_country_"):
            await show_full_country_details(update, context)
        elif data.startswith("full_realtime_"):
            await show_full_realtime_cards(update, context)
        elif data.startswith("full_random_"):
            await handle_full_random_purchase(update, context)
        elif data.startswith("full_pick_"):
            await show_full_pick_cards(update, context)
        elif data == "english":
            await set_language_english(update, context)
        elif data == "chinese":
            await set_language_chinese(update, context)
        elif data == "price_info":
            await show_price_info(update, context)
        elif data == "account_recharge":
            await show_account_recharge(update, context)
        elif data == "check_balance":
            await check_balance(update, context)
        elif data == "transaction_history":
            await show_transaction_history(update, context)
        elif data == "manual_recharge":
            await manual_recharge(update, context)
        elif data == "stock_query":
            await show_stock_query(update, context)
        elif data == "card_favorites":
            await show_card_favorites(update, context)
        elif data == "admin_panel":
            await show_admin_panel(update, context)
        else:
            logger.warning(f"未處理的按鈕回調: {data}")
            await query.answer("功能暫未實現")
    
    except Exception as e:
        logger.error(f"處理按鈕回調時發生錯誤: {e}")
        try:
            await query.answer("操作失敗，請重試")
        except:
            pass
        try:
            await query.message.reply_text("❌ 操作失敗，請重新開始 /start")
        except:
            pass

# 顯示主選單
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 創建自定義鍵盤 - 根據截圖布局
    keyboard = [
        # 第一行：賬戶信息、賬戶充值、國家/卡頭查詢
        [
            InlineKeyboardButton("👤賬戶信息", callback_data="check_balance"),
            InlineKeyboardButton("💰賬戶充值", callback_data="account_recharge"),
            InlineKeyboardButton("🔍國家/卡頭查詢", callback_data="stock_query")
        ],
        # 第二行：全資料、裸料、商家基地
        [
            InlineKeyboardButton("📊全資料", callback_data="full_fund"),
            InlineKeyboardButton("📋裸料", callback_data="naked_stock"),
            InlineKeyboardButton("🏪商家基地", callback_data="browse")
        ],
        # 第三行：售價信息、卡頭庫存、卡頭收藏
        [
            InlineKeyboardButton("💵售價信息", callback_data="price_info"),
            InlineKeyboardButton("📦卡頭庫存", callback_data="stock_query"),
            InlineKeyboardButton("⭐卡頭收藏", callback_data="card_favorites")
        ],
        # 第四行：English、聯繫客服、商家面板
        [
            InlineKeyboardButton("🌐English", callback_data="english"),
            InlineKeyboardButton("💬聯繫客服", callback_data="support"),
            InlineKeyboardButton("🛠️商家面板", callback_data="admin_panel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = await safe_edit_message(query, "請選擇功能：", reply_markup)
    
    # 更新訊息ID
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    context.chat_data['user_data']['last_message_id'] = message.message_id

# 顯示幫助
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    help_text = """
📖 使用說明

1️⃣ 選擇地區和卡片
2️⃣ 確認購買並付款
3️⃣ 收到卡片信息
4️⃣ 妥善保存卡片資料
5️⃣ 按需使用

💳 卡片優勢：
• 即買即用
• 快速交付
• 安全可靠
• 多國支持

📱 注意事項：
• 請妥善保存卡片信息
• 付款後請上傳憑證
• 如有問題請聯繫客服
    """
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, help_text, reply_markup)

# 顯示客服
async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    support_text = f"""
💬 聯繫客服

📧 Email: {config.SUPPORT_EMAIL}
📱 Telegram: {config.SUPPORT_USERNAME}
⏰ 服務時間: 24/7

常見問題請先查看使用說明
緊急問題請直接聯繫客服
    """
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, support_text, reply_markup)

# 顯示我的訂單
async def show_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    user_id = update.effective_user.id
    orders = get_user_orders(user_id)
    
    if not orders:
        text = "您還沒有訂單"
    else:
        text = "📋 您的訂單：\n\n"
        for order in orders:
            order_id, card_number, country, order_time, status = order
            status_emoji = "✅" if status == "completed" else "⏳"
            masked_number = card_number[:4] + "*" * 8 + card_number[-4:]
            text += f"{status_emoji} 訂單 #{order_id}\n"
            text += f"卡號: {masked_number}\n"
            text += f"國家: {country}\n"
            text += f"時間: {order_time[:19]}\n"
            text += "➖➖➖➖➖➖➖➖➖\n"
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 處理圖片消息（付款憑證）
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # 通知管理員收到付款憑證
    admin_text = f"""
📸 收到付款憑證

用戶: {user.first_name} (@{user.username})
用戶ID: {user.id}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

請查看並確認付款。
    """
    
    # 轉發圖片給所有管理員
    for admin_id in config.ADMIN_IDS:
        try:
            await context.bot.forward_message(
                chat_id=admin_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            await context.bot.send_message(chat_id=admin_id, text=admin_text)
        except Exception as e:
            logger.error(f"無法轉發給管理員 {admin_id}: {e}")
    
    await update.message.reply_text("✅ 付款憑證已收到，我們將盡快為您確認訂單。")

# 處理文本消息
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理用戶發送的文本消息"""
    user_data = context.user_data
    text = update.message.text.strip()
    
    # 檢查是否在等待充值金額輸入
    if user_data.get('waiting_for_recharge_amount'):
        try:
            amount = float(text)
            
            # 檢查最小充值金額
            if amount < 20:
                await update.message.reply_text(
                    "❌ 充值金額不能少於 20 USDT\n\n請重新輸入充值金額："
                )
                return
            
            # 檢查最大充值金額（可選）
            if amount > 10000:
                await update.message.reply_text(
                    "❌ 單次充值金額不能超過 10,000 USDT\n\n請重新輸入充值金額："
                )
                return
            
            # 清除等待狀態
            user_data['waiting_for_recharge_amount'] = False
            
            # 顯示充值地址
            await show_recharge_address(update, context, amount)
            
        except ValueError:
            await update.message.reply_text(
                "❌ 請輸入有效的數字金額\n\n例如：50 或 100.5\n\n請重新輸入："
            )
    else:
        # 如果不在特定狀態，顯示幫助信息
        await update.message.reply_text(
            "🤖 請使用選單按鈕進行操作\n\n如需幫助，請點擊 /start 重新開始"
        )

# 新增功能處理函數

# 裸庫功能
async def show_naked_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 獲取所有可用國家和庫存統計 - 從cards表（裸庫）
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT country, COUNT(*) as count, MIN(price) as min_price, MAX(price) as max_price
                 FROM cards 
                 WHERE status = 'available' 
                 GROUP BY country 
                 ORDER BY count DESC""")
    countries_data = c.fetchall()
    conn.close()
    
    # 國家代碼映射
    country_codes = {
        'UNITED STATES': 'US',
        'JAPAN': 'JP', 
        'SOUTH KOREA': 'KR',
        'UNITED KINGDOM': 'UK',
        'GERMANY': 'DE',
        'FRANCE': 'FR',
        'AUSTRALIA': 'AU',
        'CANADA': 'CA',
        'SINGAPORE': 'SG',
        'PHILIPPINES': 'PH'
    }
    
    if not countries_data:
        text = "❌ 暫無可用庫存"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    else:
        text = "請選擇您要購買的國家卡片：\n\n"
        
        keyboard = []
        for country, count, min_price, max_price in countries_data:
            # 獲取國家代碼
            code = country_codes.get(country, country[:2])
            
            # 根據價格範圍設置質量等級
            if min_price == max_price:
                price_range = f"${min_price:.2f}"
            else:
                price_range = f"${min_price:.2f}-${max_price:.2f}"
            
            # 設置質量等級（根據價格）
            if max_price >= 15:
                quality = "高質 C 80-90%"
                emoji = "🔥"
            elif max_price >= 10:
                quality = "高質 D 60-80%"
                emoji = ""
            else:
                quality = "高質 C 50-70%"
                emoji = ""
            
            button_text = f"高質 {code} C 60-80% {emoji} 庫存:{count} 售價:{price_range}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"naked_country_{country}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 裸庫國家詳情
async def show_naked_country_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 從callback_data中提取國家名
    country = query.data.replace("naked_country_", "")
    
    # 獲取該國家的所有可用卡片統計 - 從cards表（裸庫）
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT COUNT(*), MIN(price), MAX(price) 
                 FROM cards 
                 WHERE country = ? AND status = 'available'""", (country,))
    count, min_price, max_price = c.fetchone()
    
    # 獲取不同價格區間的統計
    c.execute("""SELECT price, COUNT(*) 
                 FROM cards 
                 WHERE country = ? AND status = 'available' 
                 GROUP BY price 
                 ORDER BY price""", (country,))
    price_stats = c.fetchall()
    conn.close()
    
    # 國家代碼映射
    country_codes = {
        'UNITED STATES': 'US',
        'JAPAN': 'JP', 
        'SOUTH KOREA': 'KR',
        'UNITED KINGDOM': 'UK',
        'GERMANY': 'DE',
        'FRANCE': 'FR',
        'AUSTRALIA': 'AU',
        'CANADA': 'CA',
        'SINGAPORE': 'SG',
        'PHILIPPINES': 'PH'
    }
    
    if count == 0:
        text = f"❌ {country} 暫無可用卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回裸庫", callback_data="naked_stock")]]
    else:
        code = country_codes.get(country, country[:2])
        
        # 構建詳細信息文本
        text = f"當前區域: 高質 {code} C 60-80%\n\n"
        
        # 顯示價格信息
        text += f"💰 價格信息:\n"
        text += f"隨機購買: $2.50 USDT\n"
        text += f"挑選購買: ${max_price:.2f} USDT\n\n"
        
        # 添加隨機多張價格選項
        if count >= 3:
            text += f"隨機3張: $7.00 USDT\n"
        if count >= 4:
            text += f"隨機4張: $8.00 USDT\n"
        if count >= 5:
            text += f"隨機5張: $8.00 USDT\n"
        
        text += f"\n📦 庫存數量: {count}張\n\n"
        text += "請選擇購買方式："
        
        # 構建按鈕
        keyboard = [
            [InlineKeyboardButton("實時卡頭", callback_data=f"realtime_{country}")],
            [
                InlineKeyboardButton("隨機購買", callback_data=f"random_buy_{country}"),
                InlineKeyboardButton("挑頭", callback_data=f"pick_card_{country}")
            ]
        ]
        
        # 添加隨機數量選項
        random_row = []
        if count >= 3:
            random_row.append(InlineKeyboardButton("隨機3頭", callback_data=f"random_3_{country}"))
        if count >= 4:
            random_row.append(InlineKeyboardButton("隨機4頭", callback_data=f"random_4_{country}"))
        if len(random_row) > 0:
            keyboard.append(random_row)
        
        if count >= 5:
            keyboard.append([InlineKeyboardButton("隨機5頭", callback_data=f"random_5_{country}")])
        
        keyboard.append([InlineKeyboardButton("返回上一步", callback_data="naked_stock")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 實時卡頭功能
async def show_realtime_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    country = query.data.replace("realtime_", "")
    
    # 獲取該國家的所有可用卡片 - 從cards表（裸庫）
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT id, card_number, expiry_date, security_code, price 
                 FROM cards 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY price ASC 
                 LIMIT 10""", (country,))
    cards = c.fetchall()
    conn.close()
    
    country_codes = {
        'UNITED STATES': 'US', 'JAPAN': 'JP', 'SOUTH KOREA': 'KR',
        'UNITED KINGDOM': 'UK', 'GERMANY': 'DE', 'FRANCE': 'FR',
        'AUSTRALIA': 'AU', 'CANADA': 'CA', 'SINGAPORE': 'SG', 'PHILIPPINES': 'PH'
    }
    
    code = country_codes.get(country, country[:2])
    text = f"🌍 {code} 實時卡頭\n\n"
    
    keyboard = []
    for card_id, card_number, expiry_date, security_code, price in cards:
        masked_number = card_number[:4] + "****" + card_number[-4:]
        button_text = f"💳 {masked_number} | {expiry_date} | ${price:.2f}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_card_{card_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回上一步", callback_data=f"naked_country_{country}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 隨機購買功能
async def handle_random_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    data = query.data
    if data.startswith("random_buy_"):
        country = data.replace("random_buy_", "")
        quantity = 1
    elif data.startswith("random_"):
        parts = data.split("_")
        quantity = int(parts[1])
        country = "_".join(parts[2:])
    
    # 獲取隨機卡片 - 從cards表（裸庫）
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT id, card_number, expiry_date, security_code, price 
                 FROM cards 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY RANDOM() 
                 LIMIT ?""", (country, quantity))
    cards = c.fetchall()
    conn.close()
    
    if not cards:
        text = f"❌ {country} 暫無可用卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回", callback_data=f"naked_country_{country}")]]
    else:
        # 計算總價 - 隨機購買使用特殊價格
        if quantity == 1:
            total_price = 2.50  # 單張隨機購買價格
        elif quantity == 3:
            total_price = 7.00
        elif quantity == 4:
            total_price = 8.00
        elif quantity == 5:
            total_price = 8.00
        else:
            total_price = quantity * 2.50  # 多張按單價計算
        
        text = f"🎲 隨機選中 {quantity} 張卡片\n\n"
        text += f"隨機購買總價: ${total_price:.2f} USDT\n\n"
        text += "選中的卡片:\n"
        
        for card_id, card_number, expiry_date, security_code, price in cards:
            masked_number = card_number[:4] + "****" + card_number[-4:]
            single_price = 2.50 if quantity == 1 else total_price / quantity
            text += f"💳 {masked_number} | {expiry_date} | ${single_price:.2f}\n"
        
        text += "\n確認購買嗎？"
        
        # 將卡片ID列表存儲在callback_data中
        card_ids = ",".join(str(card[0]) for card in cards)
        keyboard = [
            [InlineKeyboardButton("✅ 確認購買", callback_data=f"confirm_random_{card_ids}")],
            [InlineKeyboardButton("🔙 返回", callback_data=f"naked_country_{country}")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 挑頭功能
async def show_pick_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    country = query.data.replace("pick_card_", "")
    
    # 獲取該國家的所有可用卡片 - 從cards表（裸庫）
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT id, card_number, expiry_date, security_code, price 
                 FROM cards 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY price ASC""", (country,))
    cards = c.fetchall()
    conn.close()
    
    country_codes = {
        'UNITED STATES': 'US', 'JAPAN': 'JP', 'SOUTH KOREA': 'KR',
        'UNITED KINGDOM': 'UK', 'GERMANY': 'DE', 'FRANCE': 'FR',
        'AUSTRALIA': 'AU', 'CANADA': 'CA', 'SINGAPORE': 'SG', 'PHILIPPINES': 'PH'
    }
    
    code = country_codes.get(country, country[:2])
    text = f"🎯 {code} 挑頭選擇\n\n請選擇您要購買的卡片："
    
    keyboard = []
    for card_id, card_number, expiry_date, security_code, price in cards[:20]:  # 限制顯示20張
        # 顯示完整卡號前6位和後4位
        display_number = card_number[:6] + "****" + card_number[-4:]
        button_text = f"💳 {display_number} | {expiry_date} | ${price:.2f}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_card_{card_id}")])
    
    if len(cards) > 20:
        keyboard.append([InlineKeyboardButton(f"📋 查看更多 ({len(cards)-20} 張)", callback_data=f"more_cards_{country}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回上一步", callback_data=f"naked_country_{country}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 處理多卡片購買
async def handle_multiple_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, card_ids):
    query = update.callback_query
    
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # 獲取卡片詳情
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    card_details = []
    total_price = 0
    
    # 檢查是否是隨機購買（從callback_data判斷）
    is_random_purchase = "random" in query.data
    
    for card_id in card_ids:
        # 先嘗試從cards表查找
        c.execute("SELECT * FROM cards WHERE id = ? AND status = 'available'", (int(card_id),))
        card = c.fetchone()
        if card:
            card_details.append(('naked', card))
            # 根據購買方式設置價格
            if is_random_purchase:
                total_price += 2.50  # 隨機購買價格
            else:
                total_price += card[5]  # 挑選購買使用原價格
        else:
            # 如果不在cards表，嘗試full_data表
            c.execute("SELECT * FROM full_data WHERE id = ? AND status = 'available'", (int(card_id),))
            card = c.fetchone()
            if card:
                card_details.append(('full', card))
                if is_random_purchase:
                    total_price += 4.00  # 全資料隨機購買價格
                else:
                    total_price += card[6]  # 全資料挑選購買價格
    
    if not card_details:
        text = "❌ 選中的卡片已不可用"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    else:
        # 創建訂單
        order_ids = []
        for card_type, card in card_details:
            order_id = create_order(user_id, username, card[0], card_type)
            if order_id:
                order_ids.append(order_id)
        
        if order_ids:
            text = f"""
✅ 訂單創建成功！

📋 訂單詳情：
"""
            for i, (card_type, card) in enumerate(card_details):
                if card_type == 'naked':
                    card_id, card_number, expiry_date, security_code, country, price, status, created_time = card
                    actual_price = 2.50 if is_random_purchase else price
                    card_info = ""
                else:  # full
                    card_id, card_number, expiry_date, security_code, country, personal_info, price, status, created_time = card
                    actual_price = 4.00 if is_random_purchase else price
                    card_info = f"個人信息: {personal_info[:50]}...\n"
                
                purchase_type = "隨機購買" if is_random_purchase else "挑選購買"
                text += f"""
💳 卡片 {i+1} ({card_type}):
卡號: {card_number}
到期: {expiry_date}
密鑰: {security_code}
國家: {country}
{card_info}價格: ${actual_price:.2f} ({purchase_type})
➖➖➖➖➖➖➖➖➖
"""
            
            text += f"""
💰 總金額: ${total_price:.2f} USDT
📱 付款地址: {config.USDT_ADDRESS}

請轉賬後上傳付款憑證
            """
            
            keyboard = [
                [InlineKeyboardButton("📸 上傳付款憑證", callback_data=f"upload_payment_{','.join(map(str, order_ids))}")],
                [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
            ]
            
            # 通知管理員
            admin_text = f"""
🛒 新的多卡片訂單

用戶: {username} (ID: {user_id})
卡片數量: {len(card_details)}
總金額: ${total_price:.2f} USDT
訂單ID: {', '.join(map(str, order_ids))}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            for admin_id in config.ADMIN_IDS:
                try:
                    await context.bot.send_message(chat_id=admin_id, text=admin_text)
                except Exception as e:
                    logger.error(f"無法通知管理員 {admin_id}: {e}")
        else:
            text = "❌ 訂單創建失敗，請重試"
            keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    
    conn.close()
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 特價功能
async def show_special_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 獲取低價卡片 - 從兩個表中查詢
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cards WHERE status = 'available' AND price < 15")
    naked_special = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM full_data WHERE status = 'available' AND price < 20")
    full_special = c.fetchone()[0]
    special_cards = naked_special + full_special
    conn.close()
    
    text = f"""
🔥 特價卡頭

特價卡片: {special_cards} 張
價格低於 $15 的優質卡頭

限時優惠，數量有限！
    """
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 全資功能
async def show_full_fund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 獲取全資料庫存統計
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT country, COUNT(*) as count, MIN(price) as min_price, MAX(price) as max_price
                 FROM full_data 
                 WHERE status = 'available' 
                 GROUP BY country 
                 ORDER BY count DESC""")
    countries_data = c.fetchall()
    conn.close()
    
    if not countries_data:
        text = "❌ 暫無可用全資料庫存"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    else:
        text = "💰 全資料卡頭庫存\n\n"
        
        keyboard = []
        for country, count, min_price, max_price in countries_data:
            if min_price == max_price:
                price_range = f"${min_price:.2f}"
            else:
                price_range = f"${min_price:.2f}-${max_price:.2f}"
            
            button_text = f"🌍 {country} | 庫存:{count} | {price_range}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"full_country_{country}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 全資料國家詳情
async def show_full_country_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 從callback_data中提取國家名
    country = query.data.replace("full_country_", "")
    
    # 獲取該國家的全資料卡片統計
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT COUNT(*), MIN(price), MAX(price) 
                 FROM full_data 
                 WHERE country = ? AND status = 'available'""", (country,))
    count, min_price, max_price = c.fetchone()
    
    # 獲取不同價格區間的統計
    c.execute("""SELECT price, COUNT(*) 
                 FROM full_data 
                 WHERE country = ? AND status = 'available' 
                 GROUP BY price 
                 ORDER BY price""", (country,))
    price_stats = c.fetchall()
    conn.close()
    
    if count == 0:
        text = f"❌ {country} 暫無可用全資料卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回全資料", callback_data="full_fund")]]
    else:
        text = f"💰 {country} 全資料卡頭\n\n"
        
        # 顯示價格信息
        text += f"💰 價格信息:\n"
        text += f"隨機購買: $4.00 USDT\n"
        text += f"挑選購買: ${max_price:.2f} USDT\n\n"
        
        text += f"📦 庫存數量: {count}張\n\n"
        text += "💎 全資料包含完整個人信息，適合高級用途\n\n"
        text += "請選擇購買方式："
        
        # 構建按鈕
        keyboard = [
            [InlineKeyboardButton("🔍 查看實時卡頭", callback_data=f"full_realtime_{country}")],
            [
                InlineKeyboardButton("🎲 隨機購買", callback_data=f"full_random_{country}"),
                InlineKeyboardButton("🎯 挑選卡頭", callback_data=f"full_pick_{country}")
            ],
            [InlineKeyboardButton("🔙 返回全資料", callback_data="full_fund")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 全資料實時卡頭
async def show_full_realtime_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    country = query.data.replace("full_realtime_", "")
    
    # 獲取該國家的全資料卡片
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT id, card_number, expiry_date, security_code, price, personal_info 
                 FROM full_data 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY price ASC 
                 LIMIT 10""", (country,))
    cards = c.fetchall()
    conn.close()
    
    text = f"💰 {country} 全資料實時卡頭\n\n"
    
    keyboard = []
    for card_id, card_number, expiry_date, security_code, price, personal_info in cards:
        masked_number = card_number[:4] + "****" + card_number[-4:]
        # 顯示部分個人信息
        info_preview = personal_info[:30] + "..." if len(personal_info) > 30 else personal_info
        button_text = f"💳 {masked_number} | {expiry_date} | ${price:.2f}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_full_{card_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回上一步", callback_data=f"full_country_{country}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 全資料隨機購買
async def handle_full_random_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    country = query.data.replace("full_random_", "")
    
    # 隨機選擇一張卡片
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT id, card_number, expiry_date, security_code, price, personal_info 
                 FROM full_data 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY RANDOM() 
                 LIMIT 1""", (country,))
    card = c.fetchone()
    conn.close()
    
    if not card:
        text = f"❌ {country} 暫無可用全資料卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回上一步", callback_data=f"full_country_{country}")]]
    else:
        card_id, card_number, expiry_date, security_code, price, personal_info = card
        masked_number = card_number[:4] + "****" + card_number[-4:]
        
        # 隨機購買使用特殊價格
        random_price = 4.00
        
        text = f"🎲 隨機選中的全資料卡片\n\n"
        text += f"💳 卡號: {masked_number}\n"
        text += f"📅 到期: {expiry_date}\n"
        text += f"💰 隨機購買價格: ${random_price:.2f} USDT\n"
        text += f"🌍 國家: {country}\n"
        text += f"👤 個人信息預覽: {personal_info[:50]}...\n\n"
        text += "確認購買此卡片嗎？"
        
        keyboard = [
            [InlineKeyboardButton("✅ 確認購買", callback_data=f"confirm_full_{card_id}")],
            [InlineKeyboardButton("🎲 重新隨機", callback_data=f"full_random_{country}")],
            [InlineKeyboardButton("🔙 返回上一步", callback_data=f"full_country_{country}")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 全資料挑選卡頭
async def show_full_pick_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    country = query.data.replace("full_pick_", "")
    
    # 獲取該國家的全資料卡片
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT id, card_number, expiry_date, security_code, price, personal_info 
                 FROM full_data 
                 WHERE country = ? AND status = 'available' 
                 ORDER BY price ASC""", (country,))
    cards = c.fetchall()
    conn.close()
    
    text = f"🎯 {country} 全資料卡頭挑選\n\n"
    text += "請選擇您要購買的卡片："
    
    keyboard = []
    for card_id, card_number, expiry_date, security_code, price, personal_info in cards[:15]:  # 限制顯示15張
        masked_number = card_number[:4] + "****" + card_number[-4:]
        info_preview = personal_info.split('|')[0] if '|' in personal_info else personal_info[:20]
        button_text = f"💳 {masked_number} | {expiry_date} | ${price:.2f} | {info_preview}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_full_{card_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 返回上一步", callback_data=f"full_country_{country}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 處理全資料購買
async def handle_full_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, card_id: int):
    query = update.callback_query
    
    # 獲取卡片詳情
    card = get_card_details(card_id, 'full')
    
    if not card:
        await safe_edit_message(query, "❌ 卡片不存在")
        return
    
    card_id, card_number, expiry_date, security_code, country, personal_info, price, status, created_at = card
    
    if status != 'available':
        await safe_edit_message(query, "❌ 此卡片已售出")
        return
    
    masked_number = card_number[:4] + "****" + card_number[-4:]
    info_preview = personal_info[:100] + "..." if len(personal_info) > 100 else personal_info
    
    text = f"""
💰 全資料卡片詳情

💳 卡號: {masked_number}
📅 到期日期: {expiry_date}
🔒 安全碼: ***
🌍 國家: {country}
👤 個人信息: {info_preview}
💰 價格: ${price:.2f} USDT

⚠️ 購買後將顯示完整信息
確認購買此卡片嗎？
    """
    
    keyboard = [
        [InlineKeyboardButton("✅ 確認購買", callback_data=f"confirm_full_{card_id}")],
        [InlineKeyboardButton("🔙 返回", callback_data="full_fund")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 確認全資料購買
async def confirm_full_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE, card_id: int):
    query = update.callback_query
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # 檢查是否是隨機購買（從callback_data判斷）
    is_random_purchase = "random" in query.data
    
    # 檢查用戶餘額
    current_balance = wallet_manager.get_balance(user_id)
    card = get_card_details(card_id, 'full')
    
    if not card:
        await safe_edit_message(query, "❌ 卡片不存在")
        return
    
    card_id, card_number, expiry_date, security_code, country, personal_info, price, status, created_at = card
    
    if status != 'available':
        await safe_edit_message(query, "❌ 此卡片已售出")
        return
    
    # 根據購買方式設置價格
    if is_random_purchase:
        actual_price = 4.00  # 隨機購買價格
        purchase_type = "隨機購買"
    else:
        actual_price = price  # 挑選購買使用原價格
        purchase_type = "挑選購買"
    
    if current_balance < actual_price:
        text = f"""
❌ 餘額不足

當前餘額: ${current_balance:.2f} USDT
需要金額: ${actual_price:.2f} USDT ({purchase_type})
缺少金額: ${actual_price - current_balance:.2f} USDT

請先充值後再購買
        """
        keyboard = [
            [InlineKeyboardButton("💰 立即充值", callback_data="account_recharge")],
            [InlineKeyboardButton("🔙 返回", callback_data="full_fund")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text, reply_markup)
        return
    
    # 創建訂單
    order_id = create_order(user_id, username, card_id, 'full')
    
    if order_id:
        # 扣除餘額
        wallet_manager.deduct_balance(user_id, actual_price, f"{purchase_type}全資料卡片 #{card_id}")
        
        text = f"""
✅ 購買成功！

💳 卡號: {card_number}
📅 到期日期: {expiry_date}
🔒 安全碼: {security_code}
🌍 國家: {country}
👤 完整個人信息:
{personal_info}

💰 支付金額: ${actual_price:.2f} USDT ({purchase_type})
📋 訂單號: #{order_id}

⚠️ 請妥善保存此信息
        """
        
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await safe_edit_message(query, text, reply_markup)
        
        # 通知管理員
        admin_text = f"""
🛒 新的全資料訂單

用戶: {username} (ID: {user_id})
卡片: {card_number} ({country})
金額: ${actual_price:.2f} USDT ({purchase_type})
訂單ID: {order_id}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        for admin_id in config.ADMIN_IDS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=admin_text)
            except Exception as e:
                logger.error(f"無法通知管理員 {admin_id}: {e}")
    else:
        text = "❌ 訂單創建失敗，請重試"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit_message(query, text, reply_markup)

# 語言設置
async def set_language_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    text = """
🇺🇸 Language set to English

Welcome to alecc1_bot Card Robot
Robot only supports USDT
Send /start to restart conversation with me ~
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

async def set_language_chinese(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    text = """
🇨🇳 語言已設置為中文

歡迎來到 alecc1_bot 發卡機器人
機器人只支持 USDT
發送 /start 重新開始和我的對話 ~
    """
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 售價信息
async def show_price_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 獲取價格統計 - 從兩個表中查詢
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 裸庫價格統計
    c.execute("SELECT country, MIN(price), MAX(price), COUNT(*), 'naked' as type FROM cards WHERE status = 'available' GROUP BY country")
    naked_data = c.fetchall()
    
    # 全資料價格統計
    c.execute("SELECT country, MIN(price), MAX(price), COUNT(*), 'full' as type FROM full_data WHERE status = 'available' GROUP BY country")
    full_data = c.fetchall()
    
    price_data = naked_data + full_data
    conn.close()
    
    text = "💰 售價信息\n\n"
    
    text += "🔒 裸庫卡片價格:\n"
    text += "• 隨機購買: $2.50 USDT\n"
    text += "• 挑選購買: $5.00 USDT\n"
    text += "• 隨機3張: $7.00 USDT\n"
    text += "• 隨機4張: $8.00 USDT\n"
    text += "• 隨機5張: $8.00 USDT\n\n"
    
    text += "💰 全資料卡片價格:\n"
    text += "• 隨機購買: $4.00 USDT\n"
    text += "• 挑選購買: $6.00 USDT\n\n"
    
    text += "📊 庫存統計:\n"
    text += "🔒 裸庫: "
    naked_total = sum(count for _, _, _, count, card_type in price_data if card_type == 'naked')
    text += f"{naked_total}張\n"
    
    text += "💰 全資料: "
    full_total = sum(count for _, _, _, count, card_type in price_data if card_type == 'full')
    text += f"{full_total}張\n\n"
    
    text += "💳 支付方式: USDT (TRC20)\n"
    text += "💎 全資料包含完整個人信息"
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 賬戶充值
async def show_account_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # 獲取或創建用戶錢包
    wallet_manager.get_or_create_wallet(user_id, username)
    current_balance = wallet_manager.get_balance(user_id)
    
    text = f"""
💰 賬戶充值

當前餘額: ${current_balance:.2f} USDT

請輸入需要充值的金額，最小充值金額為20 USDT

請注意！充值金額以到賬金額為主，手續費自理

請直接輸入數字（例如：50）
    """
    
    # 設置用戶狀態為等待充值金額輸入
    context.user_data['waiting_for_recharge_amount'] = True
    
    keyboard = [
        [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 顯示充值地址
async def show_recharge_address(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # 為用戶分配充值地址
    recharge_address = wallet_manager.assign_usdt_address(user_id)
    
    text = f"""
💰 賬戶充值

充值金額: ${amount:.2f} USDT

📱 您的專屬充值地址：
`{recharge_address}`

充值說明：
• 僅支持TRC20網絡USDT
• 請準確轉入 ${amount:.2f} USDT
• 到賬時間：1-3個區塊確認
• 充值後自動到賬，無需聯繫客服

⚠️ 注意事項：
• 請勿使用交易所直接轉賬
• 僅支持USDT，其他幣種將丟失
• 請確認網絡為TRC20
• 手續費自理，請確保到賬金額準確
    """
    
    keyboard = [
        [InlineKeyboardButton("💳 查看餘額", callback_data="check_balance")],
        [InlineKeyboardButton("📊 交易記錄", callback_data="transaction_history")],
        [InlineKeyboardButton("🔄 手動充值", callback_data="manual_recharge")],
        [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await safe_edit_message(update.callback_query, text, reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# 查看餘額
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # 獲取錢包信息
    wallet_manager.get_or_create_wallet(user_id, username)
    balance = wallet_manager.get_balance(user_id)
    
    # 獲取錢包統計
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT total_deposited, total_spent FROM user_wallets WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    total_deposited, total_spent = result if result else (0, 0)
    conn.close()
    
    text = f"""
💳 我的錢包

當前餘額: ${balance:.2f} USDT
累計充值: ${total_deposited:.2f} USDT
累計消費: ${total_spent:.2f} USDT

錢包狀態: {'✅ 正常' if balance >= 0 else '⚠️ 餘額不足'}
    """
    
    keyboard = [
        [InlineKeyboardButton("💰 立即充值", callback_data="account_recharge")],
        [InlineKeyboardButton("📊 交易記錄", callback_data="transaction_history")],
        [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 交易記錄
async def show_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    user_id = update.effective_user.id
    transactions = wallet_manager.get_transaction_history(user_id, 10)
    
    if not transactions:
        text = "📊 交易記錄\n\n暫無交易記錄"
    else:
        text = "📊 最近交易記錄\n\n"
        for tx_type, amount, balance_after, description, created_time in transactions:
            emoji = "💰" if tx_type == "deposit" else "💳" if tx_type == "purchase" else "🔄"
            sign = "+" if tx_type == "deposit" else "-"
            text += f"{emoji} {sign}${amount:.2f} - {description}\n"
            text += f"   餘額: ${balance_after:.2f} | {created_time[:16]}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("💳 查看餘額", callback_data="check_balance")],
        [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 手動充值
async def manual_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # 為用戶分配充值地址
    recharge_address = wallet_manager.assign_usdt_address(user_id)
    
    text = f"""
🔄 手動充值

如果您已經轉賬但餘額未到賬，請：

1️⃣ 確認轉賬網絡為 TRC20
2️⃣ 確認轉賬地址：
`{recharge_address}`

3️⃣ 提供交易哈希(TXID)給客服
4️⃣ 等待人工處理（通常5-10分鐘）

💬 客服聯繫方式：
Telegram: @your_support_bot
    """
    
    keyboard = [
        [InlineKeyboardButton("📞 聯繫客服", callback_data="support")],
        [InlineKeyboardButton("🔙 返回充值", callback_data="account_recharge")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup, parse_mode='Markdown')

# 庫存查詢
async def show_stock_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 獲取庫存統計
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT country, COUNT(*) FROM products WHERE status = 'available' GROUP BY country ORDER BY COUNT(*) DESC")
    stock_data = c.fetchall()
    conn.close()
    
    text = "📊 庫存卡頭查詢\n\n"
    total = 0
    for country, count in stock_data:
        text += f"{country}: {count} 張\n"
        total += count
    
    text += f"\n總計: {total} 張卡片"
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 卡頭收藏
async def show_card_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    text = """
⭐ 卡頭收藏

您還沒有收藏任何卡頭
瀏覽卡片時可以添加到收藏夾

收藏功能即將上線...
    """
    
    keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_edit_message(query, text, reply_markup)

# 商家面板
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    # 檢查是否為管理員
    if user_id not in config.ADMIN_IDS:
        text = """
🛠️ 商家面板

抱歉，您沒有權限訪問商家面板
如需申請商家權限，請聯繫客服

💬 客服聯繫方式：
Telegram: @your_support_bot
        """
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
    else:
        # 獲取統計數據
        conn = sqlite3.connect(config.DATABASE_NAME)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM orders WHERE date(order_time) = date('now')")
        today_orders = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM products WHERE status = 'available'")
        available_cards = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM products WHERE status = 'sold'")
        sold_cards = c.fetchone()[0]
        
        c.execute("SELECT COUNT(DISTINCT user_id) FROM orders")
        total_customers = c.fetchone()[0]
        
        c.execute("SELECT SUM(total_deposited) FROM user_wallets")
        total_deposits = c.fetchone()[0] or 0
        
        conn.close()
        
        text = f"""
🛠️ 商家面板

📊 今日統計：
• 今日訂單：{today_orders} 筆
• 可用卡片：{available_cards} 張
• 已售卡片：{sold_cards} 張
• 總客戶數：{total_customers} 人
• 總充值額：${total_deposits:.2f} USDT

⚙️ 管理功能：
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 詳細統計", callback_data="admin_stats")],
            [InlineKeyboardButton("💳 錢包管理", callback_data="wallet_admin")],
            [InlineKeyboardButton("📦 庫存管理", callback_data="stock_admin")],
            [InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit_message(query, text, reply_markup)

# 管理員命令
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in config.ADMIN_IDS:
        return
    
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 獲取統計數據
    c.execute("SELECT COUNT(*) FROM orders WHERE date(order_time) = date('now')")
    today_orders = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM products WHERE status = 'available'")
    available_cards = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM products WHERE status = 'sold'")
    sold_cards = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT user_id) FROM orders")
    total_customers = c.fetchone()[0]
    
    conn.close()
    
    stats_text = f"""
📊 系統統計

今日訂單: {today_orders}
可用卡片: {available_cards}
已售卡片: {sold_cards}
總客戶數: {total_customers}
    """
    
    await update.message.reply_text(stats_text)

# 主函數
def main():
    # 初始化數據庫
    init_db()
    
    # 從配置文件獲取 bot token
    TOKEN = config.BOT_TOKEN
    
    # Bot Token 已設置
    
    # 創建應用
    application = Application.builder().token(TOKEN).build()
    
    # 添加處理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    print("🚀 Bot 正在啟動...")
    print(f"📊 管理員 ID: {config.ADMIN_IDS}")
    print("✅ Bot 已啟動，等待用戶消息...")
    
    # 啟動 bot
    application.run_polling()

if __name__ == '__main__':
    main()
