#!/usr/bin/env python3
"""
USDT 地址池初始化腳本
"""

import sqlite3
import config

def setup_usdt_addresses():
    """設置 USDT 地址池"""
    
    # 示例 USDT TRC20 地址池（⚠️ 請替換為您的真實地址）
    usdt_addresses = [
        'TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE',  # 主地址
        'TLyqzVGLV1srkB7dToTAEqgDSfPtXRJZYH',  # 地址1  
        'TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9',  # 地址2
        'TKzxdSv2FZKQrEqkKVgp5DcwEXBEKMg2Ax',  # 地址3
        'TYASr5UV6HEcXatwdFQT1HjwqjiLtqLQD6'   # 地址4
    ]
    
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    try:
        # 清空現有地址
        c.execute('DELETE FROM usdt_addresses')
        print("🗑️ 清空現有 USDT 地址")
        
        # 插入新地址
        for addr in usdt_addresses:
            c.execute('INSERT INTO usdt_addresses (address, is_used) VALUES (?, FALSE)', (addr,))
            print(f"✅ 添加地址: {addr}")
        
        conn.commit()
        print(f"\n🎉 成功設置 {len(usdt_addresses)} 個 USDT 地址")
        
        # 顯示當前地址池狀態
        c.execute('SELECT address, is_used FROM usdt_addresses')
        addresses = c.fetchall()
        
        print("\n📋 當前 USDT 地址池:")
        for addr, is_used in addresses:
            status = "🔴 已使用" if is_used else "🟢 可用"
            print(f"  {addr} - {status}")
            
    except Exception as e:
        print(f"❌ 設置失敗: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    setup_usdt_addresses() 