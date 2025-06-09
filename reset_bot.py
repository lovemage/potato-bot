#!/usr/bin/env python3
"""
重置Telegram Bot狀態
"""
import asyncio
import config
from telegram import Bot

async def reset_bot():
    """重置Bot狀態"""
    bot = Bot(token=config.BOT_TOKEN)
    
    try:
        # 刪除webhook
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook已刪除")
        
        # 獲取Bot信息
        me = await bot.get_me()
        print(f"✅ Bot信息: @{me.username}")
        
        # 清除待處理的更新
        updates = await bot.get_updates(offset=-1, limit=1)
        if updates:
            last_update_id = updates[0].update_id
            await bot.get_updates(offset=last_update_id + 1, limit=100)
            print("✅ 已清除待處理的更新")
        
        print("✅ Bot狀態重置完成")
        
    except Exception as e:
        print(f"❌ 重置失敗: {e}")
    
    finally:
        # 關閉Bot連接
        await bot.close()

if __name__ == "__main__":
    asyncio.run(reset_bot()) 