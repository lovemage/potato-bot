#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
導入數據管理工具
用於查看和管理已導入的全資料和裸庫數據
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple

class ImportedDataManager:
    def __init__(self, db_path='esim_bot.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect_db(self):
        """連接數據庫"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close_db(self):
        """關閉數據庫連接"""
        if self.conn:
            self.conn.close()
            
    def show_statistics(self):
        """顯示數據統計"""
        self.connect_db()
        
        print("📊 數據庫統計信息")
        print("=" * 60)
        
        # 全資料統計
        self.cursor.execute('SELECT COUNT(*) FROM full_data')
        full_total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM full_data WHERE status = "available"')
        full_available = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM full_data WHERE status = "sold"')
        full_sold = self.cursor.fetchone()[0]
        
        print(f"🔒 全資料卡片:")
        print(f"   總計: {full_total} 張")
        print(f"   可用: {full_available} 張")
        print(f"   已售: {full_sold} 張")
        
        # 裸庫統計
        self.cursor.execute('SELECT COUNT(*) FROM cards')
        bare_total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM cards WHERE status = "available"')
        bare_available = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM cards WHERE status = "sold"')
        bare_sold = self.cursor.fetchone()[0]
        
        print(f"\n📊 裸庫卡片:")
        print(f"   總計: {bare_total} 張")
        print(f"   可用: {bare_available} 張")
        print(f"   已售: {bare_sold} 張")
        
        print(f"\n📈 總計: {full_total + bare_total} 張卡片")
        
        self.close_db()
        
    def show_countries(self, data_type='both'):
        """顯示國家分佈"""
        self.connect_db()
        
        print(f"\n🌍 國家分佈 ({data_type})")
        print("=" * 60)
        
        if data_type in ['both', 'full']:
            print("🔒 全資料卡片:")
            self.cursor.execute('''
                SELECT country, COUNT(*) as total,
                       SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
                       SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold
                FROM full_data 
                GROUP BY country 
                ORDER BY total DESC
            ''')
            
            for country, total, available, sold in self.cursor.fetchall():
                print(f"   {country}: {total} 張 (可用: {available}, 已售: {sold})")
                
        if data_type in ['both', 'cards']:
            print("\n📊 裸庫卡片:")
            self.cursor.execute('''
                SELECT country, COUNT(*) as total,
                       SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available,
                       SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold
                FROM cards 
                GROUP BY country 
                ORDER BY total DESC
            ''')
            
            for country, total, available, sold in self.cursor.fetchall():
                print(f"   {country}: {total} 張 (可用: {available}, 已售: {sold})")
                
        self.close_db()
        
    def show_cards_by_country(self, country, data_type='both', limit=10):
        """顯示特定國家的卡片"""
        self.connect_db()
        
        print(f"\n💳 {country} 卡片詳情 (最多顯示 {limit} 張)")
        print("=" * 80)
        
        if data_type in ['both', 'full']:
            print("🔒 全資料卡片:")
            self.cursor.execute('''
                SELECT id, card_number, expiry_date, security_code, price, status, personal_info
                FROM full_data 
                WHERE country = ? 
                ORDER BY id 
                LIMIT ?
            ''', (country, limit))
            
            for i, (card_id, card_number, expiry_date, security_code, price, status, personal_info) in enumerate(self.cursor.fetchall(), 1):
                status_icon = "✅" if status == "available" else "❌"
                print(f"   {i}. {status_icon} ID:{card_id} | {card_number[:4]}****{card_number[-4:]} | {expiry_date} | {security_code} | ${price:.2f}")
                if personal_info:
                    info_preview = personal_info[:100] + "..." if len(personal_info) > 100 else personal_info
                    print(f"      👤 {info_preview}")
                print()
                
        if data_type in ['both', 'cards']:
            print("📊 裸庫卡片:")
            self.cursor.execute('''
                SELECT id, card_number, expiry_date, security_code, price, status
                FROM cards 
                WHERE country = ? 
                ORDER BY id 
                LIMIT ?
            ''', (country, limit))
            
            for i, (card_id, card_number, expiry_date, security_code, price, status) in enumerate(self.cursor.fetchall(), 1):
                status_icon = "✅" if status == "available" else "❌"
                print(f"   {i}. {status_icon} ID:{card_id} | {card_number[:4]}****{card_number[-4:]} | {expiry_date} | {security_code} | ${price:.2f}")
                
        self.close_db()
        
    def search_cards(self, keyword, data_type='both', limit=20):
        """搜索卡片"""
        self.connect_db()
        
        print(f"\n🔍 搜索結果: '{keyword}' (最多顯示 {limit} 張)")
        print("=" * 80)
        
        if data_type in ['both', 'full']:
            print("🔒 全資料卡片:")
            self.cursor.execute('''
                SELECT id, card_number, expiry_date, security_code, country, price, status
                FROM full_data 
                WHERE card_number LIKE ? OR country LIKE ? OR personal_info LIKE ?
                ORDER BY id 
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
            
            for card_id, card_number, expiry_date, security_code, country, price, status in self.cursor.fetchall():
                status_icon = "✅" if status == "available" else "❌"
                print(f"   {status_icon} ID:{card_id} | {card_number[:4]}****{card_number[-4:]} | {expiry_date} | {security_code} | {country} | ${price:.2f}")
                
        if data_type in ['both', 'cards']:
            print("\n📊 裸庫卡片:")
            self.cursor.execute('''
                SELECT id, card_number, expiry_date, security_code, country, price, status
                FROM cards 
                WHERE card_number LIKE ? OR country LIKE ?
                ORDER BY id 
                LIMIT ?
            ''', (f'%{keyword}%', f'%{keyword}%', limit))
            
            for card_id, card_number, expiry_date, security_code, country, price, status in self.cursor.fetchall():
                status_icon = "✅" if status == "available" else "❌"
                print(f"   {status_icon} ID:{card_id} | {card_number[:4]}****{card_number[-4:]} | {expiry_date} | {security_code} | {country} | ${price:.2f}")
                
        self.close_db()
        
    def update_card_status(self, card_id, data_type, new_status):
        """更新卡片狀態"""
        self.connect_db()
        
        table_name = 'full_data' if data_type == 'full' else 'cards'
        
        self.cursor.execute(f'UPDATE {table_name} SET status = ? WHERE id = ?', (new_status, card_id))
        
        if self.cursor.rowcount > 0:
            print(f"✅ 成功更新 {data_type} 卡片 ID:{card_id} 狀態為: {new_status}")
            self.conn.commit()
        else:
            print(f"❌ 找不到 {data_type} 卡片 ID:{card_id}")
            
        self.close_db()
        
    def update_card_price(self, card_id, data_type, new_price):
        """更新卡片價格"""
        self.connect_db()
        
        table_name = 'full_data' if data_type == 'full' else 'cards'
        
        self.cursor.execute(f'UPDATE {table_name} SET price = ? WHERE id = ?', (new_price, card_id))
        
        if self.cursor.rowcount > 0:
            print(f"✅ 成功更新 {data_type} 卡片 ID:{card_id} 價格為: ${new_price:.2f}")
            self.conn.commit()
        else:
            print(f"❌ 找不到 {data_type} 卡片 ID:{card_id}")
            
        self.close_db()
        
    def delete_card(self, card_id, data_type):
        """刪除卡片"""
        self.connect_db()
        
        table_name = 'full_data' if data_type == 'full' else 'cards'
        
        # 先獲取卡片信息
        self.cursor.execute(f'SELECT card_number, country FROM {table_name} WHERE id = ?', (card_id,))
        result = self.cursor.fetchone()
        
        if result:
            card_number, country = result
            confirm = input(f"⚠️  確定要刪除 {data_type} 卡片 {card_number[:4]}****{card_number[-4:]} ({country}) 嗎？(y/N): ")
            
            if confirm.lower() == 'y':
                self.cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (card_id,))
                print(f"✅ 成功刪除 {data_type} 卡片 ID:{card_id}")
                self.conn.commit()
            else:
                print("❌ 取消刪除操作")
        else:
            print(f"❌ 找不到 {data_type} 卡片 ID:{card_id}")
            
        self.close_db()
        
    def export_cards(self, country=None, data_type='both', status='available'):
        """導出卡片數據"""
        self.connect_db()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if data_type in ['both', 'full']:
            filename = f"full_data_{country or 'all'}_{status}_{timestamp}.txt"
            
            query = 'SELECT card_number, expiry_date, security_code, country, price, personal_info FROM full_data WHERE status = ?'
            params = [status]
            
            if country:
                query += ' AND country = ?'
                params.append(country)
                
            self.cursor.execute(query, params)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"全資料卡片導出 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for card_number, expiry_date, security_code, country, price, personal_info in self.cursor.fetchall():
                    f.write(f"卡號: {card_number}\n")
                    f.write(f"到期: {expiry_date}\n")
                    f.write(f"安全碼: {security_code}\n")
                    f.write(f"國家: {country}\n")
                    f.write(f"價格: ${price:.2f}\n")
                    if personal_info:
                        f.write(f"個人信息: {personal_info}\n")
                    f.write("-" * 40 + "\n\n")
                    
            print(f"✅ 全資料導出完成: {filename}")
            
        if data_type in ['both', 'cards']:
            filename = f"cards_{country or 'all'}_{status}_{timestamp}.txt"
            
            query = 'SELECT card_number, expiry_date, security_code, country, price FROM cards WHERE status = ?'
            params = [status]
            
            if country:
                query += ' AND country = ?'
                params.append(country)
                
            self.cursor.execute(query, params)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"裸庫卡片導出 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for card_number, expiry_date, security_code, country, price in self.cursor.fetchall():
                    f.write(f"{card_number} {expiry_date} {security_code} {country} ${price:.2f}\n")
                    
            print(f"✅ 裸庫導出完成: {filename}")
            
        self.close_db()

def main():
    """主函數"""
    manager = ImportedDataManager()
    
    while True:
        print("\n🛠️  導入數據管理工具")
        print("=" * 50)
        print("1. 📊 顯示統計信息")
        print("2. 🌍 顯示國家分佈")
        print("3. 💳 查看特定國家卡片")
        print("4. 🔍 搜索卡片")
        print("5. ✏️  更新卡片狀態")
        print("6. 💰 更新卡片價格")
        print("7. 🗑️  刪除卡片")
        print("8. 📤 導出卡片數據")
        print("0. 🚪 退出")
        
        choice = input("\n請選擇操作 (0-8): ").strip()
        
        if choice == '0':
            print("👋 再見！")
            break
        elif choice == '1':
            manager.show_statistics()
        elif choice == '2':
            data_type = input("數據類型 (full/cards/both): ").strip() or 'both'
            manager.show_countries(data_type)
        elif choice == '3':
            country = input("請輸入國家名稱: ").strip()
            data_type = input("數據類型 (full/cards/both): ").strip() or 'both'
            limit = int(input("顯示數量 (默認10): ").strip() or 10)
            manager.show_cards_by_country(country, data_type, limit)
        elif choice == '4':
            keyword = input("請輸入搜索關鍵字: ").strip()
            data_type = input("數據類型 (full/cards/both): ").strip() or 'both'
            limit = int(input("顯示數量 (默認20): ").strip() or 20)
            manager.search_cards(keyword, data_type, limit)
        elif choice == '5':
            card_id = int(input("請輸入卡片ID: ").strip())
            data_type = input("數據類型 (full/cards): ").strip()
            new_status = input("新狀態 (available/sold/reserved): ").strip()
            manager.update_card_status(card_id, data_type, new_status)
        elif choice == '6':
            card_id = int(input("請輸入卡片ID: ").strip())
            data_type = input("數據類型 (full/cards): ").strip()
            new_price = float(input("新價格: ").strip())
            manager.update_card_price(card_id, data_type, new_price)
        elif choice == '7':
            card_id = int(input("請輸入卡片ID: ").strip())
            data_type = input("數據類型 (full/cards): ").strip()
            manager.delete_card(card_id, data_type)
        elif choice == '8':
            country = input("國家 (留空為全部): ").strip() or None
            data_type = input("數據類型 (full/cards/both): ").strip() or 'both'
            status = input("狀態 (available/sold/all): ").strip() or 'available'
            manager.export_cards(country, data_type, status)
        else:
            print("❌ 無效選擇，請重試")

if __name__ == '__main__':
    main() 