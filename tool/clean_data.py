#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據清理工具
修復國家分類和數據質量問題
"""

import sqlite3
import re

class DataCleaner:
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
            
    def extract_country_from_personal_info(self, personal_info: str) -> str:
        """從個人信息中提取國家名稱"""
        if not personal_info:
            return 'OTHER'
            
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
        elif 'AUSTRALIA' in info or 'AU' in info:
            return 'AUSTRALIA'
        elif 'GERMANY' in info:
            return 'GERMANY'
        elif 'FRANCE' in info:
            return 'FRANCE'
        elif 'ITALY' in info:
            return 'ITALY'
        elif 'SPAIN' in info:
            return 'SPAIN'
        elif 'NETHERLANDS' in info:
            return 'NETHERLANDS'
        elif 'BELGIUM' in info:
            return 'BELGIUM'
        elif 'SWITZERLAND' in info:
            return 'SWITZERLAND'
        elif 'SWEDEN' in info:
            return 'SWEDEN'
        elif 'NORWAY' in info:
            return 'NORWAY'
        elif 'DENMARK' in info:
            return 'DENMARK'
        elif 'FINLAND' in info:
            return 'FINLAND'
        elif 'POLAND' in info:
            return 'POLAND'
        elif 'CZECH' in info:
            return 'CZECH REPUBLIC'
        elif 'SLOVAKIA' in info:
            return 'SLOVAKIA'
        elif 'SLOVENIA' in info:
            return 'SLOVENIA'
        elif 'CROATIA' in info:
            return 'CROATIA'
        elif 'SERBIA' in info:
            return 'SERBIA'
        elif 'BULGARIA' in info:
            return 'BULGARIA'
        elif 'GREECE' in info:
            return 'GREECE'
        elif 'TURKEY' in info:
            return 'TURKEY'
        elif 'RUSSIA' in info:
            return 'RUSSIA'
        elif 'UKRAINE' in info:
            return 'UKRAINE'
        elif 'BELARUS' in info:
            return 'BELARUS'
        elif 'LITHUANIA' in info:
            return 'LITHUANIA'
        elif 'LATVIA' in info:
            return 'LATVIA'
        elif 'CHINA' in info:
            return 'CHINA'
        elif 'TAIWAN' in info:
            return 'TAIWAN'
        elif 'THAILAND' in info:
            return 'THAILAND'
        elif 'VIETNAM' in info:
            return 'VIETNAM'
        elif 'MALAYSIA' in info:
            return 'MALAYSIA'
        elif 'INDONESIA' in info:
            return 'INDONESIA'
        elif 'INDIA' in info:
            return 'INDIA'
        elif 'PAKISTAN' in info:
            return 'PAKISTAN'
        elif 'BANGLADESH' in info:
            return 'BANGLADESH'
        elif 'SRI LANKA' in info:
            return 'SRI LANKA'
        elif 'NEPAL' in info:
            return 'NEPAL'
        elif 'MYANMAR' in info:
            return 'MYANMAR'
        elif 'CAMBODIA' in info:
            return 'CAMBODIA'
        elif 'LAOS' in info:
            return 'LAOS'
        elif 'BRUNEI' in info:
            return 'BRUNEI'
        elif 'NEW ZEALAND' in info:
            return 'NEW ZEALAND'
        elif 'SOUTH AFRICA' in info:
            return 'SOUTH AFRICA'
        elif 'EGYPT' in info:
            return 'EGYPT'
        elif 'MOROCCO' in info:
            return 'MOROCCO'
        elif 'TUNISIA' in info:
            return 'TUNISIA'
        elif 'ALGERIA' in info:
            return 'ALGERIA'
        elif 'NIGERIA' in info:
            return 'NIGERIA'
        elif 'KENYA' in info:
            return 'KENYA'
        elif 'GHANA' in info:
            return 'GHANA'
        elif 'ETHIOPIA' in info:
            return 'ETHIOPIA'
        elif 'BRAZIL' in info:
            return 'BRAZIL'
        elif 'ARGENTINA' in info:
            return 'ARGENTINA'
        elif 'CHILE' in info:
            return 'CHILE'
        elif 'COLOMBIA' in info:
            return 'COLOMBIA'
        elif 'PERU' in info:
            return 'PERU'
        elif 'VENEZUELA' in info:
            return 'VENEZUELA'
        elif 'ECUADOR' in info:
            return 'ECUADOR'
        elif 'BOLIVIA' in info:
            return 'BOLIVIA'
        elif 'URUGUAY' in info:
            return 'URUGUAY'
        elif 'PARAGUAY' in info:
            return 'PARAGUAY'
        elif 'MEXICO' in info:
            return 'MEXICO'
        elif 'GUATEMALA' in info:
            return 'GUATEMALA'
        elif 'COSTA RICA' in info:
            return 'COSTA RICA'
        elif 'PANAMA' in info:
            return 'PANAMA'
        elif 'NICARAGUA' in info:
            return 'NICARAGUA'
        elif 'HONDURAS' in info:
            return 'HONDURAS'
        elif 'EL SALVADOR' in info:
            return 'EL SALVADOR'
        elif 'BELIZE' in info:
            return 'BELIZE'
        elif 'JAMAICA' in info:
            return 'JAMAICA'
        elif 'CUBA' in info:
            return 'CUBA'
        elif 'DOMINICAN REPUBLIC' in info:
            return 'DOMINICAN REPUBLIC'
        elif 'HAITI' in info:
            return 'HAITI'
        elif 'PUERTO RICO' in info:
            return 'PUERTO RICO'
        elif 'TRINIDAD' in info:
            return 'TRINIDAD AND TOBAGO'
        elif 'BARBADOS' in info:
            return 'BARBADOS'
        elif 'BAHAMAS' in info:
            return 'BAHAMAS'
        elif 'ISRAEL' in info:
            return 'ISRAEL'
        elif 'PALESTINE' in info:
            return 'PALESTINE'
        elif 'JORDAN' in info:
            return 'JORDAN'
        elif 'LEBANON' in info:
            return 'LEBANON'
        elif 'SYRIA' in info:
            return 'SYRIA'
        elif 'IRAQ' in info:
            return 'IRAQ'
        elif 'IRAN' in info:
            return 'IRAN'
        elif 'AFGHANISTAN' in info:
            return 'AFGHANISTAN'
        elif 'SAUDI ARABIA' in info:
            return 'SAUDI ARABIA'
        elif 'UAE' in info or 'UNITED ARAB EMIRATES' in info:
            return 'UAE'
        elif 'QATAR' in info:
            return 'QATAR'
        elif 'KUWAIT' in info:
            return 'KUWAIT'
        elif 'BAHRAIN' in info:
            return 'BAHRAIN'
        elif 'OMAN' in info:
            return 'OMAN'
        elif 'YEMEN' in info:
            return 'YEMEN'
        else:
            return 'OTHER'
            
    def clean_bare_data_countries(self):
        """清理裸庫數據的國家分類"""
        print("🧹 清理裸庫數據國家分類...")
        
        # 獲取所有需要清理的記錄
        self.cursor.execute('SELECT id, country FROM cards')
        records = self.cursor.fetchall()
        
        updated_count = 0
        
        for record_id, country in records:
            new_country = self.normalize_country_name(country)
            
            if new_country != country:
                self.cursor.execute(
                    'UPDATE cards SET country = ? WHERE id = ?',
                    (new_country, record_id)
                )
                updated_count += 1
                
        print(f"✅ 裸庫數據更新了 {updated_count} 條記錄")
        
    def clean_full_data_countries(self):
        """清理全資料的國家分類"""
        print("🧹 清理全資料國家分類...")
        
        # 獲取所有需要清理的記錄
        self.cursor.execute('SELECT id, country, personal_info FROM full_data')
        records = self.cursor.fetchall()
        
        updated_count = 0
        
        for record_id, country, personal_info in records:
            # 如果國家是個人信息，重新提取
            if '|' in country or len(country) > 50:
                new_country = self.extract_country_from_personal_info(personal_info)
            else:
                new_country = self.normalize_country_name(country)
            
            if new_country != country:
                self.cursor.execute(
                    'UPDATE full_data SET country = ? WHERE id = ?',
                    (new_country, record_id)
                )
                updated_count += 1
                
        print(f"✅ 全資料更新了 {updated_count} 條記錄")
        
    def normalize_country_name(self, country: str) -> str:
        """標準化國家名稱"""
        if not country:
            return 'OTHER'
            
        country = country.upper().strip()
        
        # 處理特殊情況
        if 'KOREA' in country or 'REPUBLIC OF' in country:
            return 'KOREA'
        elif 'USA' in country or 'UNITED STATES' in country:
            return 'USA'
        elif 'SINGAPORE' in country:
            return 'SINGAPORE'
        elif 'HONG KONG' in country or 'HONG' in country:
            return 'HONG KONG'
        elif 'JAPAN' in country:
            return 'JAPAN'
        elif 'PHILIPPINES' in country:
            return 'PHILIPPINES'
        elif 'EMPCHECK.CO' in country:
            return 'EMPCheck.Co'
        elif 'CHECKER0.ME' in country:
            return '[CHECKER0.ME]'
        elif 'LIVE' in country and len(country) < 10:
            return 'Live'
        elif 'AUSTRIA' in country:
            return 'AUSTRIA'
        elif 'CROATIA' in country:
            return 'CROATIA'
        elif 'CANADA' in country:
            return 'CANADA'
        elif 'ROMANIA' in country:
            return 'ROMANIA'
        elif 'HUNGARY' in country:
            return 'HUNGARY'
        elif 'ESTONIA' in country:
            return 'ESTONIA'
        elif 'UK' in country or 'UNITED KINGDOM' in country or 'GB' in country:
            return 'UK'
        elif 'AUSTRALIA' in country or 'AU' in country:
            return 'AUSTRALIA'
        elif country.startswith('BIN') or country.startswith('4') or '/' in country:
            return 'OTHER'  # 這些是錯誤的分類
        elif len(country) > 30:  # 太長的可能是個人信息
            return 'OTHER'
        else:
            return country
            
    def update_prices(self):
        """更新價格"""
        print("💰 更新價格...")
        
        # 更新裸庫價格
        price_map = {
            'USA': 12.0,
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
            'UK': 12.0,
            'AUSTRALIA': 11.0
        }
        
        for country, price in price_map.items():
            self.cursor.execute(
                'UPDATE cards SET price = ? WHERE country = ?',
                (price, country)
            )
            
            # 全資料價格增加5美元
            self.cursor.execute(
                'UPDATE full_data SET price = ? WHERE country = ?',
                (price + 5.0, country)
            )
            
        print("✅ 價格更新完成")
        
    def show_cleaned_stats(self):
        """顯示清理後的統計信息"""
        print("\n📊 清理後的統計信息:")
        print("=" * 50)
        
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

def main():
    """主函數"""
    print("🧹 eSIM Bot 數據清理工具")
    print("=" * 50)
    
    cleaner = DataCleaner()
    cleaner.connect_db()
    
    # 清理數據
    cleaner.clean_bare_data_countries()
    cleaner.clean_full_data_countries()
    cleaner.update_prices()
    
    # 提交更改
    cleaner.conn.commit()
    
    # 顯示清理後的統計
    cleaner.show_cleaned_stats()
    
    print("\n✅ 數據清理完成!")
    
    cleaner.close_db()

if __name__ == '__main__':
    main() 