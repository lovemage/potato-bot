#!/usr/bin/env python3
"""
測試Bot連接
"""
import asyncio
import config
from telegram import Bot

async def test_connection():
    """測試Bot連接"""
    bot = Bot(token=config.BOT_TOKEN)
    
    try:
        print("🔍 測試Bot連接...")
        
        # 獲取Bot信息
        me = await bot.get_me()
        print(f"✅ Bot信息: @{me.username} ({me.first_name})")
        
        # 嘗試獲取更新（這會顯示是否有衝突）
        print("🔍 測試獲取更新...")
        updates = await bot.get_updates(limit=1, timeout=5)
        print(f"✅ 成功獲取更新，數量: {len(updates)}")
        
        print("✅ Bot連接測試成功！")
        
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")
        if "Conflict" in str(e):
            print("⚠️  檢測到衝突：可能有其他Bot實例在運行")
            print("   請檢查是否有其他服務器或進程在使用同一個Bot token")
    
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_connection()) 