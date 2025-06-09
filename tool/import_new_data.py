#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新數據導入工具 v0.6.7
用於處理 data/ 目錄中的裸庫和全資庫數據文件
將數據分別導入到數據庫中並進行分類
"""

import sqlite3
import re
import os
from datetime import datetime
from typing import List, Dict, Tuple

class NewDataImporter:
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
            
    def create_tables(self):
        """創建必要的數據表"""
        # 創建卡片表（裸庫數據）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT UNIQUE NOT NULL,
                expiry_date TEXT NOT NULL,
                security_code TEXT NOT NULL,
                country TEXT NOT NULL,
                price REAL DEFAULT 10.0,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 創建全資料表（包含個人信息）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS full_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT UNIQUE NOT NULL,
                expiry_date TEXT NOT NULL,
                security_code TEXT NOT NULL,
                country TEXT NOT NULL,
                personal_info TEXT,
                price REAL DEFAULT 15.0,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def parse_bare_card_line(self, line: str) -> Tuple[str, str, str, str]:
        """解析裸庫卡片信息行
        格式: 卡號|到期日期|安全碼|國家信息
        """
        if '|' in line:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                card_number = parts[0].strip()
                expiry_date = parts[1].strip()
                security_code = parts[2].strip()
                country_info = parts[3].strip()
                
                # 提取國家名稱（去除額外信息）
                country = self.extract_country_name(country_info)
                return card_number, expiry_date, security_code, country
        return None, None, None, None
        
    def parse_full_card_line(self, line: str) -> Tuple[str, str, str, str, str]:
        """解析全資料卡片信息行
        格式: 卡號|到期日期|安全碼|個人信息
        """
        if '|' in line:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                card_number = parts[0].strip()
                expiry_date = parts[1].strip()
                security_code = parts[2].strip()
                personal_info = '|'.join(parts[3:]).strip()
                
                # 從個人信息中提取國家
                country = self.extract_country_from_personal_info(personal_info)
                return card_number, expiry_date, security_code, country, personal_info
        return None, None, None, None, None
        
    def extract_country_name(self, country_info: str) -> str:
        """從國家信息中提取國家名稱"""
        # 移除常見的額外信息
        country = country_info.upper()
        
        # 處理特殊標記
        if 'KOREA' in country or 'REPUBLIC OF' in country:
            return 'KOREA'
        elif 'USA' in country or 'UNITED STATES' in country:
            return 'USA'
        elif 'SINGAPORE' in country:
            return 'SINGAPORE'
        elif 'HONG KONG' in country:
            return 'HONG KONG'
        elif 'JAPAN' in country:
            return 'JAPAN'
        elif 'PHILIPPINES' in country:
            return 'PHILIPPINES'
        elif 'EMPCHECK.CO' in country:
            return 'EMPCheck.Co'
        elif 'CHECKER0.ME' in country:
            return '[CHECKER0.ME]'
        elif 'LIVE' in country:
            return 'Live'
        elif 'AUSTRIA' in country:
            return 'AUSTRIA'
        elif 'CROATIA' in country:
            return 'CROATIA'
        elif 'CANADA' in country:
            return 'CANADA'
        else:
            # 返回第一個單詞作為國家名
            words = country.split()
            return words[0] if words else 'OTHER'
            
    def extract_country_from_personal_info(self, personal_info: str) -> str:
        """從個人信息中提取國家名稱"""
        info = personal_info.upper()
        
        # 常見國家模式
        if 'KOREA' in info or 'REPUBLIC OF' in info:
            return 'KOREA'
        elif 'USA' in info or 'UNITED STATES' in info:
            return 'USA'
        elif 'SINGAPORE' in info:
            return 'SINGAPORE'
        elif 'HONG KONG' in info:
            return 'HONG KONG'
        elif 'JAPAN' in info:
            return 'JAPAN'
        elif 'PHILIPPINES' in info:
            return 'PHILIPPINES'
        elif 'ROMANIA' in info:
            return 'ROMANIA'
        elif 'HUNGARY' in info:
            return 'HUNGARY'
        elif 'ESTONIA' in info:
            return 'ESTONIA'
        elif 'AUSTRIA' in info:
            return 'AUSTRIA'
        elif 'CANADA' in info or 'CAN' in info:
            return 'CANADA'
        elif 'UNITED KINGDOM' in info or 'GB' in info:
            return 'UK'
        else:
            return 'OTHER'
        
    def is_valid_card_number(self, card_number: str) -> bool:
        """驗證卡號格式"""
        return bool(re.match(r'^\d{13,19}$', card_number))
        
    def is_valid_expiry_date(self, expiry_date: str) -> bool:
        """驗證到期日期格式 (MM/YY)"""
        return bool(re.match(r'^\d{2}/\d{2}$', expiry_date))
        
    def is_valid_security_code(self, security_code: str) -> bool:
        """驗證安全碼格式"""
        return bool(re.match(r'^\d{3,4}$', security_code))
        
    def get_country_price(self, country: str, is_full_data: bool = False) -> float:
        """根據國家設定價格"""
        base_price_map = {
            'USA': 12.0,
            'UNITED STATES': 12.0,
            'KOREA': 8.0,
            'JAPAN': 10.0,
            'SINGAPORE': 9.0,
            'HONG KONG': 11.0,
            'PHILIPPINES': 7.0,
            'EMPCheck.Co': 5.0,
            '[CHECKER0.ME]': 5.0,
            'Live': 6.0,
            'ROMANIA': 8.0,
            'HUNGARY': 9.0,
            'ESTONIA': 9.0,
            'AUSTRIA': 11.0,
            'CANADA': 10.0,
            'UK': 12.0
        }
        
        base_price = base_price_map.get(country.upper(), 10.0)
        
        # 全資料價格增加5美元
        if is_full_data:
            base_price += 5.0
            
        return base_price
        
    def import_bare_data_file(self, file_path: str) -> int:
        """導入裸庫數據文件"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return 0
            
        print(f"📖 讀取裸庫文件: {file_path}")
        
        imported_count = 0
        current_country = ""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳過空行和標題行
                if not line or line.startswith('=') or 'Bare Data' in line:
                    continue
                    
                # 檢查是否是國家標題行
                if line.startswith('[') and line.endswith(')'):
                    # 提取國家名稱 [KOREA] (26 records)
                    country_match = re.match(r'\[([^\]]+)\]', line)
                    if country_match:
                        current_country = country_match.group(1)
                    continue
                    
                # 檢查是否是分隔線
                if line.startswith('---') or line.startswith('-'):
                    continue
                    
                # 解析卡片信息
                card_number, expiry_date, security_code, country = self.parse_bare_card_line(line)
                
                if not card_number:
                    continue
                    
                # 使用當前國家或解析出的國家
                final_country = country if country and country != 'OTHER' else current_country
                
                # 驗證數據
                if not (self.is_valid_card_number(card_number) and 
                       self.is_valid_expiry_date(expiry_date) and 
                       self.is_valid_security_code(security_code)):
                    print(f"⚠️  第{line_num}行無效數據: {line[:50]}...")
                    continue
                    
                # 設定價格
                price = self.get_country_price(final_country, False)
                
                try:
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO cards 
                        (card_number, expiry_date, security_code, country, price, status)
                        VALUES (?, ?, ?, ?, ?, 'available')
                    ''', (card_number, expiry_date, security_code, final_country, price))
                    
                    if self.cursor.rowcount > 0:
                        imported_count += 1
                        if imported_count % 50 == 0:
                            print(f"✅ 已導入裸庫: {imported_count} 條")
                        
                except sqlite3.Error as e:
                    print(f"❌ 第{line_num}行導入失敗: {e}")
                    
        return imported_count
        
    def import_full_data_file(self, file_path: str) -> int:
        """導入全資料文件"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return 0
            
        print(f"📖 讀取全資料文件: {file_path}")
        
        imported_count = 0
        current_country = ""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳過空行和標題行
                if not line or line.startswith('=') or 'Full Data' in line:
                    continue
                    
                # 檢查是否是國家標題行
                if line.startswith('[') and line.endswith(')'):
                    # 提取國家名稱 [KOREA] (2 records)
                    country_match = re.match(r'\[([^\]]+)\]', line)
                    if country_match:
                        current_country = country_match.group(1)
                    continue
                    
                # 檢查是否是分隔線
                if line.startswith('---') or line.startswith('-'):
                    continue
                    
                # 解析卡片信息
                card_number, expiry_date, security_code, country, personal_info = self.parse_full_card_line(line)
                
                if not card_number:
                    continue
                    
                # 使用解析出的國家或當前國家
                final_country = country if country and country != 'OTHER' else current_country
                
                # 驗證數據
                if not (self.is_valid_card_number(card_number) and 
                       self.is_valid_expiry_date(expiry_date) and 
                       self.is_valid_security_code(security_code)):
                    print(f"⚠️  第{line_num}行無效數據: {line[:50]}...")
                    continue
                    
                # 設定價格（全資料價格較高）
                price = self.get_country_price(final_country, True)
                
                try:
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO full_data 
                        (card_number, expiry_date, security_code, country, personal_info, price, status)
                        VALUES (?, ?, ?, ?, ?, ?, 'available')
                    ''', (card_number, expiry_date, security_code, final_country, personal_info, price))
                    
                    if self.cursor.rowcount > 0:
                        imported_count += 1
                        if imported_count % 50 == 0:
                            print(f"✅ 已導入全資料: {imported_count} 條")
                        
                except sqlite3.Error as e:
                    print(f"❌ 第{line_num}行導入失敗: {e}")
                    
        return imported_count
        
    def show_statistics(self):
        """顯示數據庫統計信息"""
        print("\n📊 數據庫統計信息:")
        print("=" * 60)
        
        # 全資料統計
        self.cursor.execute('SELECT COUNT(*) FROM full_data')
        full_total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT country, COUNT(*) FROM full_data GROUP BY country ORDER BY COUNT(*) DESC')
        full_by_country = self.cursor.fetchall()
        
        print(f"🔒 全資料總計: {full_total} 條")
        for country, count in full_by_country:
            print(f"   {country}: {count} 條")
            
        # 裸庫統計
        self.cursor.execute('SELECT COUNT(*) FROM cards')
        bare_total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT country, COUNT(*) FROM cards GROUP BY country ORDER BY COUNT(*) DESC')
        bare_by_country = self.cursor.fetchall()
        
        print(f"\n📊 裸庫總計: {bare_total} 條")
        for country, count in bare_by_country:
            print(f"   {country}: {count} 條")
            
        print(f"\n📈 數據庫總計: {full_total + bare_total} 條記錄")
        
        # 價格統計
        self.cursor.execute('SELECT AVG(price) FROM full_data')
        avg_full_price = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('SELECT AVG(price) FROM cards')
        avg_bare_price = self.cursor.fetchone()[0] or 0
        
        print(f"\n💰 價格統計:")
        print(f"   全資料平均價格: ${avg_full_price:.2f}")
        print(f"   裸庫平均價格: ${avg_bare_price:.2f}")

def main():
    """主函數"""
    print("🚀 eSIM Bot 新數據導入工具 v0.6.7")
    print("=" * 60)
    
    importer = NewDataImporter()
    
    # 連接數據庫並創建表
    importer.connect_db()
    importer.create_tables()
    
    print("\n🔄 開始導入數據...")
    
    # 導入裸庫數據
    bare_file = 'data/a_裸库_v0.6.7.txt'
    bare_count = importer.import_bare_data_file(bare_file)
    
    # 導入全資料
    full_file = 'data/b_全资库_v0.6.7.txt'
    full_count = importer.import_full_data_file(full_file)
    
    # 提交更改
    importer.conn.commit()
    
    # 顯示統計信息
    importer.show_statistics()
    
    print(f"\n✅ 導入完成!")
    print(f"📊 裸庫導入: {bare_count} 條")
    print(f"📋 全資料導入: {full_count} 條")
    print(f"📈 總計導入: {bare_count + full_count} 條")
    
    importer.close_db()

if __name__ == '__main__':
    main() 