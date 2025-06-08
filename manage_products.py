#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
卡片管理工具
用於管理卡片的添加、修改、刪除和查看
"""

import sqlite3
import sys
from datetime import datetime
import config

class CardManager:
    def __init__(self):
        self.db_name = config.DATABASE_NAME
    
    def add_card(self, card_number, expiry_date, security_code, country, price):
        """添加新卡片"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("""INSERT INTO products 
                         (card_number, expiry_date, security_code, country, price)
                         VALUES (?, ?, ?, ?, ?)""",
                      (card_number, expiry_date, security_code, country, price))
            conn.commit()
            card_id = c.lastrowid
            conn.close()
            print(f"✅ 卡片已成功添加，ID: {card_id}")
            print(f"   卡號: {card_number}")
            print(f"   國家: {country}")
            print(f"   價格: ${price}")
            return card_id
        except sqlite3.IntegrityError:
            print(f"❌ 卡號 {card_number} 已存在")
            return None
        except Exception as e:
            print(f"❌ 添加卡片失敗: {str(e)}")
            return None
    
    def list_cards(self, country=None):
        """列出所有卡片或特定國家的卡片"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            if country:
                c.execute("""SELECT * FROM products WHERE country = ? ORDER BY price""", (country,))
                print(f"\n💳 {country} 的卡片:")
            else:
                c.execute("""SELECT * FROM products ORDER BY country, price""")
                print("\n💳 所有卡片:")
            
            cards = c.fetchall()
            conn.close()
            
            if not cards:
                print("   暫無卡片")
                return
            
            print("-" * 120)
            print(f"{'ID':<4} {'卡號':<18} {'到期日':<8} {'密鑰':<6} {'國家':<15} {'價格':<8} {'狀態':<10} {'創建時間':<20}")
            print("-" * 120)
            
            for card in cards:
                id, card_number, expiry_date, security_code, country, price, status, created_time = card
                status_emoji = "✅" if status == "available" else "❌" if status == "sold" else "⏳"
                print(f"{id:<4} {card_number:<18} {expiry_date:<8} {security_code:<6} {country:<15} ${price:<7.2f} {status_emoji} {status:<8} {created_time[:19]:<20}")
            
            print("-" * 120)
            print(f"總計: {len(cards)} 張卡片")
            
        except Exception as e:
            print(f"❌ 查詢卡片失敗: {str(e)}")
    
    def update_price(self, card_id, new_price):
        """更新卡片價格"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # 檢查卡片是否存在
            c.execute("SELECT card_number FROM products WHERE id = ?", (card_id,))
            result = c.fetchone()
            
            if not result:
                print(f"❌ 找不到 ID 為 {card_id} 的卡片")
                conn.close()
                return False
            
            # 更新價格
            c.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, card_id))
            conn.commit()
            conn.close()
            
            print(f"✅ 卡片 '{result[0]}' 的價格已更新為 ${new_price}")
            return True
            
        except Exception as e:
            print(f"❌ 更新價格失敗: {str(e)}")
            return False
    
    def update_status(self, card_id, new_status):
        """更新卡片狀態"""
        valid_statuses = ["available", "sold", "reserved"]
        
        if new_status not in valid_statuses:
            print(f"❌ 無效的狀態: {new_status}")
            print(f"有效狀態: {', '.join(valid_statuses)}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # 檢查卡片是否存在
            c.execute("SELECT card_number FROM products WHERE id = ?", (card_id,))
            result = c.fetchone()
            
            if not result:
                print(f"❌ 找不到 ID 為 {card_id} 的卡片")
                conn.close()
                return False
            
            # 更新狀態
            c.execute("UPDATE products SET status = ? WHERE id = ?", (new_status, card_id))
            conn.commit()
            conn.close()
            
            print(f"✅ 卡片 '{result[0]}' 的狀態已更新為 {new_status}")
            return True
            
        except Exception as e:
            print(f"❌ 更新狀態失敗: {str(e)}")
            return False
    
    def delete_card(self, card_id):
        """刪除卡片"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # 檢查卡片是否存在
            c.execute("SELECT card_number FROM products WHERE id = ?", (card_id,))
            result = c.fetchone()
            
            if not result:
                print(f"❌ 找不到 ID 為 {card_id} 的卡片")
                conn.close()
                return False
            
            # 確認刪除
            confirm = input(f"⚠️  確定要刪除卡片 '{result[0]}' 嗎？(y/N): ")
            if confirm.lower() != 'y':
                print("❌ 取消刪除")
                conn.close()
                return False
            
            # 刪除卡片
            c.execute("DELETE FROM products WHERE id = ?", (card_id,))
            conn.commit()
            conn.close()
            
            print(f"✅ 卡片 '{result[0]}' 已刪除")
            return True
            
        except Exception as e:
            print(f"❌ 刪除卡片失敗: {str(e)}")
            return False
    
    def get_countries(self):
        """獲取所有國家列表"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT DISTINCT country FROM products ORDER BY country")
            countries = [row[0] for row in c.fetchall()]
            conn.close()
            return countries
        except Exception as e:
            print(f"❌ 獲取國家列表失敗: {str(e)}")
            return []
    
    def import_from_text(self, text_data):
        """從文本批量導入卡片"""
        lines = text_data.strip().split('\n')
        success_count = 0
        error_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                parts = line.split('|')
                if len(parts) != 4:
                    print(f"❌ 格式錯誤: {line}")
                    error_count += 1
                    continue
                
                card_number, expiry_date, security_code, country = parts
                # 根據國家設置默認價格
                price = self.get_default_price(country)
                
                if self.add_card(card_number, expiry_date, security_code, country, price):
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ 處理行失敗: {line} - {e}")
                error_count += 1
        
        print(f"\n📊 導入結果: 成功 {success_count} 張，失敗 {error_count} 張")
    
    def get_default_price(self, country):
        """根據國家獲取默認價格"""
        price_map = {
            'UNITED STATES': 15.0,
            'JAPAN': 12.0,
            'SOUTH KOREA': 10.0,
            'UNITED KINGDOM': 18.0,
            'FRANCE': 16.0,
            'GERMANY': 16.0,
            'CANADA': 14.0,
            'AUSTRALIA': 20.0,
            'SINGAPORE': 13.0,
        }
        return price_map.get(country, 10.0)

def show_help():
    """顯示幫助信息"""
    print("""
💳 卡片管理工具

使用方法:
  python3 manage_products.py [命令] [參數]

命令:
  list                    - 列出所有卡片
  list [國家]             - 列出特定國家的卡片
  add                     - 交互式添加新卡片
  import                  - 從文件批量導入卡片
  price [ID] [價格]       - 更新卡片價格
  status [ID] [狀態]      - 更新卡片狀態
  delete [ID]             - 刪除卡片
  countries               - 列出所有國家
  help                    - 顯示此幫助信息

卡片狀態:
  available  - 可用
  sold       - 已售出
  reserved   - 已預留

示例:
  python3 manage_products.py list
  python3 manage_products.py list "UNITED STATES"
  python3 manage_products.py add
  python3 manage_products.py price 1 25.99
  python3 manage_products.py status 1 sold
    """)

def interactive_add_card(manager):
    """交互式添加卡片"""
    print("\n💳 添加新卡片")
    print("-" * 30)
    
    try:
        card_number = input("卡號: ").strip()
        if not card_number:
            print("❌ 卡號不能為空")
            return
        
        expiry_date = input("到期日 (MM/YY): ").strip()
        if not expiry_date:
            print("❌ 到期日不能為空")
            return
        
        security_code = input("密鑰: ").strip()
        if not security_code:
            print("❌ 密鑰不能為空")
            return
        
        country = input("國家: ").strip().upper()
        if not country:
            print("❌ 國家不能為空")
            return
        
        price = input("價格 (USD): ").strip()
        try:
            price = float(price)
            if price <= 0:
                print("❌ 價格必須大於 0")
                return
        except ValueError:
            print("❌ 價格必須是數字")
            return
        
        # 確認信息
        print(f"\n📋 卡片信息確認:")
        print(f"   卡號: {card_number}")
        print(f"   到期日: {expiry_date}")
        print(f"   密鑰: {security_code}")
        print(f"   國家: {country}")
        print(f"   價格: ${price}")
        
        confirm = input("\n確認添加此卡片？(y/N): ")
        if confirm.lower() == 'y':
            manager.add_card(card_number, expiry_date, security_code, country, price)
        else:
            print("❌ 取消添加")
            
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")

def import_from_file(manager):
    """從文件導入卡片"""
    filename = input("請輸入文件名 (或直接粘貼數據，以空行結束): ").strip()
    
    if filename:
        # 嘗試讀取文件
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.read()
            print(f"📁 正在從文件 {filename} 導入...")
            manager.import_from_text(data)
            return
        except FileNotFoundError:
            print(f"❌ 文件 {filename} 不存在")
            print("💡 請確認文件路徑是否正確")
        except Exception as e:
            print(f"❌ 讀取文件失敗: {e}")
    
    # 如果文件讀取失敗，則手動輸入
    print("請粘貼卡片數據 (格式: 號碼|日期|密鑰|國家)，以空行結束:")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    
    if lines:
        data = '\n'.join(lines)
        manager.import_from_text(data)
    else:
        print("❌ 沒有輸入數據")

def main():
    manager = CardManager()
    
    if len(sys.argv) == 1:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_help()
    
    elif command == "list":
        if len(sys.argv) > 2:
            country = sys.argv[2]
            manager.list_cards(country)
        else:
            manager.list_cards()
    
    elif command == "add":
        interactive_add_card(manager)
    
    elif command == "import":
        import_from_file(manager)
    
    elif command == "price":
        if len(sys.argv) != 4:
            print("❌ 用法: python3 manage_products.py price [卡片ID] [新價格]")
            return
        
        try:
            card_id = int(sys.argv[2])
            new_price = float(sys.argv[3])
            manager.update_price(card_id, new_price)
        except ValueError:
            print("❌ 卡片ID必須是數字，價格必須是數字")
    
    elif command == "status":
        if len(sys.argv) != 4:
            print("❌ 用法: python3 manage_products.py status [卡片ID] [新狀態]")
            return
        
        try:
            card_id = int(sys.argv[2])
            new_status = sys.argv[3]
            manager.update_status(card_id, new_status)
        except ValueError:
            print("❌ 卡片ID必須是數字")
    
    elif command == "delete":
        if len(sys.argv) != 3:
            print("❌ 用法: python3 manage_products.py delete [卡片ID]")
            return
        
        try:
            card_id = int(sys.argv[2])
            manager.delete_card(card_id)
        except ValueError:
            print("❌ 卡片ID必須是數字")
    
    elif command == "countries":
        countries = manager.get_countries()
        if countries:
            print("\n🌍 可用國家/地區:")
            for i, country in enumerate(countries, 1):
                print(f"  {i}. {country}")
        else:
            print("❌ 暫無卡片數據")
    
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main() 