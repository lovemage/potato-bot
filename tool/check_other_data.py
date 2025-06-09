#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查OTHER分類的數據樣本
"""

import sqlite3

def check_other_data():
    """檢查被分類為OTHER的數據"""
    conn = sqlite3.connect('esim_bot.db')
    cursor = conn.cursor()
    
    print('🔍 檢查OTHER分類的數據樣本:')
    print('=' * 50)
    
    print('\n📊 裸庫OTHER樣本:')
    cursor.execute('SELECT card_number, country FROM cards WHERE country = "OTHER" LIMIT 5')
    for card_number, country in cursor.fetchall():
        print(f'   {card_number[:4]}****{card_number[-4:]} | {country}')
    
    print('\n🔒 全資料OTHER樣本:')
    cursor.execute('SELECT card_number, country, personal_info FROM full_data WHERE country = "OTHER" LIMIT 3')
    for card_number, country, personal_info in cursor.fetchall():
        print(f'   {card_number[:4]}****{card_number[-4:]} | {country}')
        print(f'      個人信息: {personal_info[:100]}...')
    
    # 檢查所有唯一的國家名稱
    print('\n🌍 所有唯一的國家/地區 (裸庫):')
    cursor.execute('SELECT DISTINCT country FROM cards ORDER BY country')
    bare_countries = [row[0] for row in cursor.fetchall()]
    for country in bare_countries:
        print(f'   {country}')
    
    print('\n🌍 所有唯一的國家/地區 (全資料):')
    cursor.execute('SELECT DISTINCT country FROM full_data ORDER BY country')
    full_countries = [row[0] for row in cursor.fetchall()]
    for i, country in enumerate(full_countries):
        if i < 20:  # 只顯示前20個
            print(f'   {country}')
        elif i == 20:
            print(f'   ... 還有 {len(full_countries) - 20} 個')
            break
    
    conn.close()

if __name__ == '__main__':
    check_other_data() 