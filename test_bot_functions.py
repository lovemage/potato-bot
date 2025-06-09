#!/usr/bin/env python3
"""
測試Bot功能
"""
import asyncio
import sqlite3
import config
from wallet_manager import WalletManager

async def test_bot_functions():
    """測試Bot的各項功能"""
    print("🤖 開始測試Bot功能...")
    
    # 初始化錢包管理器
    wallet_manager = WalletManager()
    
    # 測試用戶
    test_user_id = 67890
    test_username = "test_user"
    
    print(f"\n1. 測試用戶錢包創建:")
    wallet = wallet_manager.get_or_create_wallet(test_user_id, test_username)
    print(f"   ✅ 用戶錢包已創建: ID={wallet[1]}, 餘額=${wallet[3]:.2f}")
    
    print(f"\n2. 測試充值流程:")
    # 模擬充值
    success, new_balance = wallet_manager.add_balance(test_user_id, 100.0, "測試充值", test_username)
    if success:
        print(f"   ✅ 充值成功，新餘額: ${new_balance:.2f}")
    else:
        print(f"   ❌ 充值失敗")
    
    print(f"\n3. 測試隨機購買價格計算:")
    test_quantities = [1, 3, 4, 5, 10]
    for qty in test_quantities:
        if qty == 1:
            price = 2.50
        elif qty == 3:
            price = 7.00
        elif qty == 4:
            price = 8.00
        elif qty == 5:
            price = 8.00
        else:
            price = qty * 2.50
        print(f"   {qty}張: ${price:.2f} USDT")
    
    print(f"\n4. 測試數據庫查詢:")
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 檢查裸庫
    c.execute("SELECT country, COUNT(*) FROM cards WHERE status = 'available' GROUP BY country LIMIT 5")
    naked_countries = c.fetchall()
    print(f"   裸庫前5個國家:")
    for country, count in naked_countries:
        print(f"     - {country}: {count}張")
    
    # 檢查全資料
    c.execute("SELECT country, COUNT(*) FROM full_data WHERE status = 'available' GROUP BY country LIMIT 5")
    full_countries = c.fetchall()
    print(f"   全資料前5個國家:")
    for country, count in full_countries:
        print(f"     - {country}: {count}張")
    
    conn.close()
    
    print(f"\n5. 測試購買流程模擬:")
    # 模擬隨機購買1張美國卡
    c = conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM cards WHERE country = 'UNITED STATES' AND status = 'available' LIMIT 1")
    card = c.fetchone()
    
    if card:
        card_id = card[0]
        purchase_price = 2.50
        
        # 檢查餘額
        current_balance = wallet_manager.get_balance(test_user_id)
        if current_balance >= purchase_price:
            # 模擬扣款
            success, remaining_balance, message = wallet_manager.deduct_balance(
                test_user_id, purchase_price, f"購買美國卡片 ID:{card_id}", test_username
            )
            if success:
                print(f"   ✅ 購買成功，剩餘餘額: ${remaining_balance:.2f}")
                # 標記卡片為已售出（測試用，實際不執行）
                print(f"   📝 應標記卡片 {card_id} 為已售出")
            else:
                print(f"   ❌ 購買失敗: {message}")
        else:
            print(f"   ❌ 餘額不足: ${current_balance:.2f} < ${purchase_price:.2f}")
    else:
        print(f"   ⚠️  沒有可用的美國卡片")
    
    conn.close()
    
    print(f"\n6. 測試QR碼生成功能:")
    try:
        import qrcode
        from io import BytesIO
        import tempfile
        
        # 生成測試QR碼
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data("tron:TQVS6n4XfzkayhjKRFQA2YdSxkW1TjAACk?amount=50")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存到臨時文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img.save(tmp_file.name)
            print(f"   ✅ QR碼生成成功: {tmp_file.name}")
            
    except Exception as e:
        print(f"   ❌ QR碼生成失敗: {e}")
    
    print(f"\n7. 測試交易記錄:")
    transactions = wallet_manager.get_transaction_history(test_user_id, 5)
    print(f"   最近5筆交易:")
    for i, (tx_type, amount, balance_after, description, timestamp) in enumerate(transactions, 1):
        print(f"     {i}. {tx_type}: ${amount:.2f} -> ${balance_after:.2f} ({description}) - {timestamp}")
    
    print(f"\n🎉 Bot功能測試完成!")
    final_balance = wallet_manager.get_balance(test_user_id)
    print(f"測試用戶最終餘額: ${final_balance:.2f} USDT")

if __name__ == "__main__":
    asyncio.run(test_bot_functions()) 