#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot 連接測試腳本
"""

import asyncio
import config
from telegram import Bot

async def test_bot_connection():
    """測試 Bot 連接"""
    try:
        bot = Bot(token=config.BOT_TOKEN)
        
        print("🔍 測試 Bot 連接...")
        
        # 獲取 Bot 信息
        bot_info = await bot.get_me()
        
        print("✅ Bot 連接成功！")
        print(f"📱 Bot 名稱: {bot_info.first_name}")
        print(f"🆔 Bot 用戶名: @{bot_info.username}")
        print(f"🔢 Bot ID: {bot_info.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot 連接失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始測試 Telegram Bot 連接...")
    
    # 運行測試
    result = asyncio.run(test_bot_connection())
    
    if result:
        print("\n🎉 測試完成！Bot 已準備就緒。")
        print("💡 您現在可以運行: python3 esim-telegram-bot.py")
    else:
        print("\n❌ 測試失敗！請檢查 Bot Token 是否正確。") 