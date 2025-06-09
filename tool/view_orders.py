#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
eSIM 訂單管理工具
用於查看和管理訂單
"""

import sqlite3
import sys
from datetime import datetime, timedelta
import config

class OrderManager:
    def __init__(self):
        self.db_name = config.DATABASE_NAME
    
    def view_recent_orders(self, limit=20):
        """查看最近的訂單"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("""
                SELECT o.id, o.user_id, o.username, p.product_name, p.price,
                       o.order_time, o.status
                FROM orders o
                JOIN products p ON o.product_id = p.id
                ORDER BY o.order_time DESC
                LIMIT ?
            """, (limit,))
            
            orders = c.fetchall()
            conn.close()
            
            if not orders:
                print("❌ 暫無訂單")
                return
            
            print(f"\n📋 最近 {len(orders)} 筆訂單:")
            print("-" * 120)
            print(f"{'訂單ID':<8} {'用戶ID':<12} {'用戶名':<15} {'產品名稱':<30} {'金額':<8} {'時間':<20} {'狀態':<10}")
            print("-" * 120)
            
            for order in orders:
                order_id, user_id, username, product_name, price, order_time, status = order
                username = username or "未知"
                status_emoji = "✅" if status == "completed" else "⏳" if status == "pending" else "❌"
                print(f"{order_id:<8} {user_id:<12} {username:<15} {product_name[:30]:<30} ${price:<7.2f} {order_time:<20} {status_emoji} {status:<8}")
            
            print("-" * 120)
            
        except Exception as e:
            print(f"❌ 查詢訂單失敗: {str(e)}")
    
    def view_orders_by_user(self, user_id):
        """查看特定用戶的訂單"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("""
                SELECT o.id, o.username, p.product_name, p.price,
                       o.order_time, o.status
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE o.user_id = ?
                ORDER BY o.order_time DESC
            """, (user_id,))
            
            orders = c.fetchall()
            conn.close()
            
            if not orders:
                print(f"❌ 用戶 {user_id} 暫無訂單")
                return
            
            print(f"\n👤 用戶 {user_id} 的訂單 (共 {len(orders)} 筆):")
            print("-" * 100)
            print(f"{'訂單ID':<8} {'用戶名':<15} {'產品名稱':<30} {'金額':<8} {'時間':<20} {'狀態':<10}")
            print("-" * 100)
            
            total_amount = 0
            for order in orders:
                order_id, username, product_name, price, order_time, status = order
                username = username or "未知"
                status_emoji = "✅" if status == "completed" else "⏳" if status == "pending" else "❌"
                print(f"{order_id:<8} {username:<15} {product_name[:30]:<30} ${price:<7.2f} {order_time:<20} {status_emoji} {status:<8}")
                if status == "completed":
                    total_amount += price
            
            print("-" * 100)
            print(f"總消費金額: ${total_amount:.2f}")
            
        except Exception as e:
            print(f"❌ 查詢用戶訂單失敗: {str(e)}")
    
    def update_order_status(self, order_id, new_status):
        """更新訂單狀態"""
        valid_statuses = ["pending", "completed", "cancelled", "refunded"]
        
        if new_status not in valid_statuses:
            print(f"❌ 無效的狀態: {new_status}")
            print(f"有效狀態: {', '.join(valid_statuses)}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # 檢查訂單是否存在
            c.execute("""
                SELECT o.id, o.user_id, p.product_name, o.status
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE o.id = ?
            """, (order_id,))
            
            result = c.fetchone()
            if not result:
                print(f"❌ 找不到訂單 ID: {order_id}")
                conn.close()
                return False
            
            old_status = result[3]
            product_name = result[2]
            
            # 更新狀態
            c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
            conn.commit()
            conn.close()
            
            print(f"✅ 訂單 #{order_id} 狀態已更新")
            print(f"   產品: {product_name}")
            print(f"   狀態: {old_status} → {new_status}")
            
            return True
            
        except Exception as e:
            print(f"❌ 更新訂單狀態失敗: {str(e)}")
            return False
    
    def get_daily_stats(self, days=7):
        """獲取每日統計"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # 獲取最近幾天的統計
            c.execute("""
                SELECT DATE(order_time) as date, 
                       COUNT(*) as order_count,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                       SUM(CASE WHEN status = 'completed' THEN p.price ELSE 0 END) as revenue
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE order_time >= datetime('now', '-{} days')
                GROUP BY DATE(order_time)
                ORDER BY date DESC
            """.format(days))
            
            stats = c.fetchall()
            conn.close()
            
            if not stats:
                print(f"❌ 最近 {days} 天暫無訂單數據")
                return
            
            print(f"\n📊 最近 {days} 天統計:")
            print("-" * 80)
            print(f"{'日期':<12} {'總訂單':<8} {'完成訂單':<10} {'完成率':<8} {'營收':<10}")
            print("-" * 80)
            
            total_orders = 0
            total_completed = 0
            total_revenue = 0
            
            for stat in stats:
                date, order_count, completed_count, revenue = stat
                completion_rate = (completed_count / order_count * 100) if order_count > 0 else 0
                revenue = revenue or 0
                
                print(f"{date:<12} {order_count:<8} {completed_count:<10} {completion_rate:<7.1f}% ${revenue:<9.2f}")
                
                total_orders += order_count
                total_completed += completed_count
                total_revenue += revenue
            
            print("-" * 80)
            overall_completion_rate = (total_completed / total_orders * 100) if total_orders > 0 else 0
            print(f"{'總計':<12} {total_orders:<8} {total_completed:<10} {overall_completion_rate:<7.1f}% ${total_revenue:<9.2f}")
            
        except Exception as e:
            print(f"❌ 獲取統計失敗: {str(e)}")
    
    def get_popular_products(self, limit=10):
        """獲取熱門產品"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            c.execute("""
                SELECT p.product_name, p.country, COUNT(*) as order_count,
                       SUM(CASE WHEN o.status = 'completed' THEN p.price ELSE 0 END) as revenue
                FROM orders o
                JOIN products p ON o.product_id = p.id
                GROUP BY p.id, p.product_name, p.country
                ORDER BY order_count DESC
                LIMIT ?
            """, (limit,))
            
            products = c.fetchall()
            conn.close()
            
            if not products:
                print("❌ 暫無產品銷售數據")
                return
            
            print(f"\n🔥 熱門產品 TOP {len(products)}:")
            print("-" * 100)
            print(f"{'排名':<4} {'產品名稱':<30} {'國家':<10} {'訂單數':<8} {'營收':<10}")
            print("-" * 100)
            
            for i, product in enumerate(products, 1):
                product_name, country, order_count, revenue = product
                revenue = revenue or 0
                print(f"{i:<4} {product_name[:30]:<30} {country:<10} {order_count:<8} ${revenue:<9.2f}")
            
            print("-" * 100)
            
        except Exception as e:
            print(f"❌ 獲取熱門產品失敗: {str(e)}")
    
    def search_orders(self, keyword):
        """搜索訂單"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # 搜索用戶名或產品名稱包含關鍵字的訂單
            c.execute("""
                SELECT o.id, o.user_id, o.username, p.product_name, p.price,
                       o.order_time, o.status
                FROM orders o
                JOIN products p ON o.product_id = p.id
                WHERE o.username LIKE ? OR p.product_name LIKE ? OR p.country LIKE ?
                ORDER BY o.order_time DESC
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            
            orders = c.fetchall()
            conn.close()
            
            if not orders:
                print(f"❌ 未找到包含 '{keyword}' 的訂單")
                return
            
            print(f"\n🔍 搜索結果 (關鍵字: '{keyword}'):")
            print("-" * 120)
            print(f"{'訂單ID':<8} {'用戶ID':<12} {'用戶名':<15} {'產品名稱':<30} {'金額':<8} {'時間':<20} {'狀態':<10}")
            print("-" * 120)
            
            for order in orders:
                order_id, user_id, username, product_name, price, order_time, status = order
                username = username or "未知"
                status_emoji = "✅" if status == "completed" else "⏳" if status == "pending" else "❌"
                print(f"{order_id:<8} {user_id:<12} {username:<15} {product_name[:30]:<30} ${price:<7.2f} {order_time:<20} {status_emoji} {status:<8}")
            
            print("-" * 120)
            print(f"找到 {len(orders)} 筆訂單")
            
        except Exception as e:
            print(f"❌ 搜索訂單失敗: {str(e)}")

def show_help():
    """顯示幫助信息"""
    print("""
📋 eSIM 訂單管理工具

使用方法:
  python3 view_orders.py [命令] [參數]

命令:
  recent [數量]           - 查看最近的訂單 (默認20筆)
  user [用戶ID]          - 查看特定用戶的所有訂單
  status [訂單ID] [狀態] - 更新訂單狀態
  stats [天數]           - 查看每日統計 (默認7天)
  popular [數量]         - 查看熱門產品 (默認10個)
  search [關鍵字]        - 搜索訂單
  help                   - 顯示此幫助信息

訂單狀態:
  pending    - 待處理
  completed  - 已完成
  cancelled  - 已取消
  refunded   - 已退款

示例:
  python3 view_orders.py recent 50
  python3 view_orders.py user 123456789
  python3 view_orders.py status 1 completed
  python3 view_orders.py stats 30
  python3 view_orders.py popular 5
  python3 view_orders.py search 日本
    """)

def main():
    manager = OrderManager()
    
    if len(sys.argv) == 1:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_help()
    
    elif command == "recent":
        limit = 20
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                print("❌ 數量必須是數字")
                return
        manager.view_recent_orders(limit)
    
    elif command == "user":
        if len(sys.argv) != 3:
            print("❌ 用法: python3 view_orders.py user [用戶ID]")
            return
        
        try:
            user_id = int(sys.argv[2])
            manager.view_orders_by_user(user_id)
        except ValueError:
            print("❌ 用戶ID必須是數字")
    
    elif command == "status":
        if len(sys.argv) != 4:
            print("❌ 用法: python3 view_orders.py status [訂單ID] [新狀態]")
            return
        
        try:
            order_id = int(sys.argv[2])
            new_status = sys.argv[3]
            manager.update_order_status(order_id, new_status)
        except ValueError:
            print("❌ 訂單ID必須是數字")
    
    elif command == "stats":
        days = 7
        if len(sys.argv) > 2:
            try:
                days = int(sys.argv[2])
            except ValueError:
                print("❌ 天數必須是數字")
                return
        manager.get_daily_stats(days)
    
    elif command == "popular":
        limit = 10
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                print("❌ 數量必須是數字")
                return
        manager.get_popular_products(limit)
    
    elif command == "search":
        if len(sys.argv) != 3:
            print("❌ 用法: python3 view_orders.py search [關鍵字]")
            return
        
        keyword = sys.argv[2]
        manager.search_orders(keyword)
    
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main() 