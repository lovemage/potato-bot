import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import config

# 設置日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        logger.warning("image.png 文件未找到，僅發送文字訊息")
        message = await update.effective_chat.send_message(welcome_text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"發送圖片失敗: {e}，改為發送文字訊息")
        message = await update.effective_chat.send_message(welcome_text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # 回應查詢
    await query.answer()
    
    if data == "naked_stock":
        text = "🔥 裸庫功能\n\n這裡顯示所有可用的卡片庫存"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "special_price":
        text = "💰 特價功能\n\n這裡顯示特價卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "full_fund":
        text = "💎 全資功能\n\n這裡顯示高額度卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "english":
        text = "🇺🇸 Language switched to English\n\nEnglish interface coming soon..."
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "chinese":
        text = "🇨🇳 已切換為中文\n\n當前已是中文界面"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "price_info":
        text = "💰 售價信息\n\n各國卡片價格範圍：\n• 美國: $10-15\n• 日本: $8-12\n• 韓國: $6-10"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "account_recharge":
        text = "💳 賬戶充值\n\n請聯繫客服進行充值"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "browse":
        text = "🛒 選頭購買\n\n瀏覽所有可用卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "stock_query":
        text = "📊 庫存查詢\n\n當前庫存統計"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "my_orders":
        text = "📋 訂單記錄\n\n您的購買記錄"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "card_favorites":
        text = "⭐ 卡頭收藏\n\n您收藏的卡片"
        keyboard = [[InlineKeyboardButton("🔙 返回主選單", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
        
    elif data == "main_menu":
        # 返回主選單
        welcome_text = f"""🌐 歡迎使用【全球 沙發CVV數據庫】

您好！{update.effective_user.first_name} 我是您的數據專屬助理馬鈴薯 🤖

我們堅持一手/二手/品質第一/堅若磐石

🇯🇵 日本 | 🇰🇷 韓國 | 🇹🇭 泰國
🇸🇬 新加坡 | 🇺🇸 美國 | 🇪🇺 歐洲
🇦🇺 澳洲 | 🇬🇧 英國 | 🇨🇳 中國

如何開始？
點擊下方按鈕，立即探索適合您的 數據 方案！"""
        
        keyboard = [
            [
                InlineKeyboardButton("裸庫❤️", callback_data="naked_stock"),
                InlineKeyboardButton("特價❤️", callback_data="special_price"),
                InlineKeyboardButton("全資❤️", callback_data="full_fund")
            ],
            [
                InlineKeyboardButton("English", callback_data="english"),
                InlineKeyboardButton("中文", callback_data="chinese"),
                InlineKeyboardButton("售價信息", callback_data="price_info"),
                InlineKeyboardButton("賬戶充值", callback_data="account_recharge")
            ],
            [
                InlineKeyboardButton("選頭購買", callback_data="browse"),
                InlineKeyboardButton("庫存卡頭查詢", callback_data="stock_query"),
                InlineKeyboardButton("訂單記錄", callback_data="my_orders"),
                InlineKeyboardButton("卡頭收藏", callback_data="card_favorites")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)

def main():
    # 從配置文件獲取 bot token
    TOKEN = config.BOT_TOKEN
    
    # 創建應用
    application = Application.builder().token(TOKEN).build()
    
    # 添加處理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("🚀 簡化測試 Bot 正在啟動...")
    print("✅ Bot 已啟動，等待用戶消息...")
    
    # 啟動 bot
    application.run_polling()

if __name__ == '__main__':
    main() 