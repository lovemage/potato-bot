#!/usr/bin/env python3
"""
測試支付系統功能
"""
import sqlite3
import config
from wallet_manager import WalletManager

def test_payment_system():
    """測試支付系統的各項功能"""
    print("🧪 開始測試支付系統...")
    
    # 初始化錢包管理器
    wallet_manager = WalletManager()
    
    # 測試用戶ID
    test_user_id = 12345
    
    print(f"\n1. 測試用戶 {test_user_id} 的初始餘額:")
    initial_balance = wallet_manager.get_balance(test_user_id)
    print(f"   初始餘額: ${initial_balance:.2f} USDT")
    
    print(f"\n2. 測試充值功能:")
    # 模擬充值 $50
    recharge_amount = 50.00
    wallet_manager.add_balance(test_user_id, recharge_amount, "測試充值")
    new_balance = wallet_manager.get_balance(test_user_id)
    print(f"   充值 ${recharge_amount:.2f} 後餘額: ${new_balance:.2f} USDT")
    
    print(f"\n3. 測試扣款功能:")
    # 模擬購買 $2.50
    purchase_amount = 2.50
    try:
        wallet_manager.deduct_balance(test_user_id, purchase_amount, "測試購買1張卡片")
        final_balance = wallet_manager.get_balance(test_user_id)
        print(f"   購買 ${purchase_amount:.2f} 後餘額: ${final_balance:.2f} USDT")
    except Exception as e:
        print(f"   ❌ 扣款失敗: {e}")
    
    print(f"\n4. 測試交易記錄:")
    transactions = wallet_manager.get_transaction_history(test_user_id)
    print(f"   交易記錄數量: {len(transactions)}")
    for i, (tx_id, amount, tx_type, description, timestamp) in enumerate(transactions[-3:], 1):
        print(f"   {i}. {tx_type}: ${amount:.2f} - {description} ({timestamp})")
    
    print(f"\n5. 測試USDT地址分配:")
    usdt_address = wallet_manager.assign_usdt_address(test_user_id)
    print(f"   分配的USDT地址: {usdt_address}")
    
    print(f"\n6. 測試餘額不足情況:")
    result = wallet_manager.deduct_balance(test_user_id, 1000.00, "測試大額購買")
    if result[0]:  # 如果扣款成功
        print("   ❌ 應該拒絕餘額不足的扣款")
    else:
        print(f"   ✅ 正確拒絕扣款: {result[2]}")
    
    print(f"\n7. 測試數據庫連接:")
    try:
        conn = sqlite3.connect(config.DATABASE_NAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM cards WHERE status = 'available'")
        available_cards = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM full_data WHERE status = 'available'")
        available_full_data = c.fetchone()[0]
        conn.close()
        print(f"   ✅ 數據庫連接正常")
        print(f"   可用裸庫: {available_cards}張")
        print(f"   可用全資料: {available_full_data}張")
    except Exception as e:
        print(f"   ❌ 數據庫連接失敗: {e}")
    
    print(f"\n8. 測試QR碼生成:")
    try:
        import qrcode
        print("   ✅ QR碼模塊可用")
    except ImportError:
        print("   ❌ QR碼模塊未安裝")
    
    print(f"\n🎉 支付系統測試完成!")
    print(f"最終用戶餘額: ${wallet_manager.get_balance(test_user_id):.2f} USDT")

if __name__ == "__main__":
    test_payment_system() 