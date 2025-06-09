#!/usr/bin/env python3
"""
錢包管理工具
供管理員手動操作用戶錢包
"""

import sqlite3
import sys
from datetime import datetime
from wallet_manager import wallet_manager
import config

def show_menu():
    """顯示主選單"""
    print("\n" + "="*50)
    print("💰 錢包管理系統")
    print("="*50)
    print("1. 查看用戶錢包")
    print("2. 手動充值")
    print("3. 手動扣款")
    print("4. 查看交易記錄")
    print("5. 查看所有錢包")
    print("6. 充值統計")
    print("0. 退出")
    print("="*50)

def view_user_wallet():
    """查看用戶錢包"""
    user_id = input("請輸入用戶ID: ").strip()
    if not user_id.isdigit():
        print("❌ 無效的用戶ID")
        return
    
    user_id = int(user_id)
    
    # 獲取錢包信息
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM user_wallets WHERE user_id = ?", (user_id,))
    wallet = c.fetchone()
    
    if wallet:
        wallet_id, user_id, username, balance, total_deposited, total_spent, created_time, updated_time = wallet
        print(f"\n💳 用戶錢包信息")
        print(f"用戶ID: {user_id}")
        print(f"用戶名: {username}")
        print(f"當前餘額: ${balance:.2f} USDT")
        print(f"累計充值: ${total_deposited:.2f} USDT")
        print(f"累計消費: ${total_spent:.2f} USDT")
        print(f"創建時間: {created_time}")
        print(f"更新時間: {updated_time}")
    else:
        print("❌ 用戶錢包不存在")
    
    conn.close()

def manual_deposit():
    """手動充值"""
    user_id = input("請輸入用戶ID: ").strip()
    if not user_id.isdigit():
        print("❌ 無效的用戶ID")
        return
    
    user_id = int(user_id)
    
    amount = input("請輸入充值金額: ").strip()
    try:
        amount = float(amount)
        if amount <= 0:
            print("❌ 充值金額必須大於0")
            return
    except ValueError:
        print("❌ 無效的金額")
        return
    
    username = input("請輸入用戶名 (可選): ").strip() or f"User_{user_id}"
    description = input("請輸入充值說明 (可選): ").strip() or "管理員手動充值"
    txid = input("請輸入交易哈希 (可選): ").strip() or None
    
    # 執行充值
    success, new_balance = wallet_manager.add_balance(user_id, username, amount, description, txid)
    
    if success:
        print(f"✅ 充值成功！新餘額: ${new_balance:.2f} USDT")
    else:
        print("❌ 充值失敗")

def manual_deduct():
    """手動扣款"""
    user_id = input("請輸入用戶ID: ").strip()
    if not user_id.isdigit():
        print("❌ 無效的用戶ID")
        return
    
    user_id = int(user_id)
    
    amount = input("請輸入扣款金額: ").strip()
    try:
        amount = float(amount)
        if amount <= 0:
            print("❌ 扣款金額必須大於0")
            return
    except ValueError:
        print("❌ 無效的金額")
        return
    
    username = input("請輸入用戶名 (可選): ").strip() or f"User_{user_id}"
    description = input("請輸入扣款說明 (可選): ").strip() or "管理員手動扣款"
    
    # 執行扣款
    success, new_balance, message = wallet_manager.deduct_balance(user_id, username, amount, description)
    
    if success:
        print(f"✅ 扣款成功！新餘額: ${new_balance:.2f} USDT")
    else:
        print(f"❌ 扣款失敗: {message}")

def view_transactions():
    """查看交易記錄"""
    user_id = input("請輸入用戶ID (留空查看所有): ").strip()
    
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    if user_id and user_id.isdigit():
        c.execute("""SELECT * FROM transactions 
                     WHERE user_id = ? 
                     ORDER BY created_time DESC 
                     LIMIT 20""", (int(user_id),))
        print(f"\n📊 用戶 {user_id} 的交易記錄:")
    else:
        c.execute("""SELECT * FROM transactions 
                     ORDER BY created_time DESC 
                     LIMIT 50""")
        print(f"\n📊 最近50筆交易記錄:")
    
    transactions = c.fetchall()
    
    if transactions:
        print("-" * 100)
        print(f"{'ID':<5} {'用戶ID':<8} {'類型':<8} {'金額':<10} {'餘額前':<10} {'餘額後':<10} {'說明':<20} {'時間':<20}")
        print("-" * 100)
        
        for tx in transactions:
            tx_id, user_id, username, tx_type, amount, balance_before, balance_after, description, txid, order_id, status, created_time = tx
            print(f"{tx_id:<5} {user_id:<8} {tx_type:<8} ${amount:<9.2f} ${balance_before:<9.2f} ${balance_after:<9.2f} {description[:18]:<20} {created_time[:19]:<20}")
    else:
        print("❌ 沒有找到交易記錄")
    
    conn.close()

def view_all_wallets():
    """查看所有錢包"""
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM user_wallets ORDER BY balance DESC")
    wallets = c.fetchall()
    
    if wallets:
        print(f"\n💳 所有用戶錢包 (共 {len(wallets)} 個):")
        print("-" * 80)
        print(f"{'用戶ID':<8} {'用戶名':<15} {'餘額':<12} {'累計充值':<12} {'累計消費':<12}")
        print("-" * 80)
        
        total_balance = 0
        total_deposited = 0
        total_spent = 0
        
        for wallet in wallets:
            wallet_id, user_id, username, balance, deposited, spent, created_time, updated_time = wallet
            print(f"{user_id:<8} {username[:14]:<15} ${balance:<11.2f} ${deposited:<11.2f} ${spent:<11.2f}")
            total_balance += balance
            total_deposited += deposited
            total_spent += spent
        
        print("-" * 80)
        print(f"{'總計':<8} {'':<15} ${total_balance:<11.2f} ${total_deposited:<11.2f} ${total_spent:<11.2f}")
    else:
        print("❌ 沒有找到錢包記錄")
    
    conn.close()

def deposit_statistics():
    """充值統計"""
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 今日充值統計
    c.execute("""SELECT COUNT(*), COALESCE(SUM(amount), 0) 
                 FROM transactions 
                 WHERE transaction_type = 'deposit' 
                 AND date(created_time) = date('now')""")
    today_count, today_amount = c.fetchone()
    
    # 本月充值統計
    c.execute("""SELECT COUNT(*), COALESCE(SUM(amount), 0) 
                 FROM transactions 
                 WHERE transaction_type = 'deposit' 
                 AND strftime('%Y-%m', created_time) = strftime('%Y-%m', 'now')""")
    month_count, month_amount = c.fetchone()
    
    # 總充值統計
    c.execute("""SELECT COUNT(*), COALESCE(SUM(amount), 0) 
                 FROM transactions 
                 WHERE transaction_type = 'deposit'""")
    total_count, total_amount = c.fetchone()
    
    print(f"\n📈 充值統計")
    print("-" * 40)
    print(f"今日充值: {today_count} 筆, ${today_amount:.2f} USDT")
    print(f"本月充值: {month_count} 筆, ${month_amount:.2f} USDT")
    print(f"總計充值: {total_count} 筆, ${total_amount:.2f} USDT")
    
    conn.close()

def main():
    """主函數"""
    print("🚀 錢包管理系統啟動")
    
    while True:
        show_menu()
        choice = input("\n請選擇操作 (0-6): ").strip()
        
        if choice == "0":
            print("👋 再見！")
            break
        elif choice == "1":
            view_user_wallet()
        elif choice == "2":
            manual_deposit()
        elif choice == "3":
            manual_deduct()
        elif choice == "4":
            view_transactions()
        elif choice == "5":
            view_all_wallets()
        elif choice == "6":
            deposit_statistics()
        else:
            print("❌ 無效的選擇，請重試")
        
        input("\n按 Enter 繼續...")

if __name__ == "__main__":
    main() 