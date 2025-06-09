#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速查看數據庫統計信息
"""

import sqlite3
from datetime import datetime

def show_database_stats():
    """顯示數據庫統計信息"""
    try:
        conn = sqlite3.connect('esim_bot.db')
        cursor = conn.cursor()
        
        print("🚀 eSIM Bot 數據庫統計信息")
        print("=" * 60)
        print(f"📅 查詢時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 全資料統計
        cursor.execute('SELECT COUNT(*) FROM full_data')
        full_total = cursor.fetchone()[0]
        
        cursor.execute('SELECT country, COUNT(*) FROM full_data GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10')
        full_by_country = cursor.fetchall()
        
        print(f"\n🔒 全資料總計: {full_total} 條")
        print("   前10個國家/地區:")
        for country, count in full_by_country:
            print(f"   {country}: {count} 條")
            
        # 裸庫統計
        cursor.execute('SELECT COUNT(*) FROM cards')
        bare_total = cursor.fetchone()[0]
        
        cursor.execute('SELECT country, COUNT(*) FROM cards GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10')
        bare_by_country = cursor.fetchall()
        
        print(f"\n📊 裸庫總計: {bare_total} 條")
        print("   前10個國家/地區:")
        for country, count in bare_by_country:
            print(f"   {country}: {count} 條")
            
        print(f"\n📈 數據庫總計: {full_total + bare_total} 條記錄")
        
        # 狀態統計
        cursor.execute('SELECT status, COUNT(*) FROM full_data GROUP BY status')
        full_status = cursor.fetchall()
        
        cursor.execute('SELECT status, COUNT(*) FROM cards GROUP BY status')
        bare_status = cursor.fetchall()
        
        print(f"\n📋 狀態統計:")
        print("   全資料:")
        for status, count in full_status:
            print(f"     {status}: {count} 條")
        print("   裸庫:")
        for status, count in bare_status:
            print(f"     {status}: {count} 條")
        
        # 價格統計
        cursor.execute('SELECT AVG(price), MIN(price), MAX(price) FROM full_data')
        full_price_stats = cursor.fetchone()
        
        cursor.execute('SELECT AVG(price), MIN(price), MAX(price) FROM cards')
        bare_price_stats = cursor.fetchone()
        
        print(f"\n💰 價格統計:")
        if full_price_stats[0]:
            print(f"   全資料: 平均 ${full_price_stats[0]:.2f}, 最低 ${full_price_stats[1]:.2f}, 最高 ${full_price_stats[2]:.2f}")
        if bare_price_stats[0]:
            print(f"   裸庫: 平均 ${bare_price_stats[0]:.2f}, 最低 ${bare_price_stats[1]:.2f}, 最高 ${bare_price_stats[2]:.2f}")
        
        # 最近添加的記錄
        cursor.execute('SELECT COUNT(*) FROM full_data WHERE date(created_at) = date("now")')
        today_full = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM cards WHERE date(created_at) = date("now")')
        today_bare = cursor.fetchone()[0]
        
        print(f"\n📅 今日新增:")
        print(f"   全資料: {today_full} 條")
        print(f"   裸庫: {today_bare} 條")
        print(f"   總計: {today_full + today_bare} 條")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ 數據庫錯誤: {e}")
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == '__main__':
    show_database_stats() 