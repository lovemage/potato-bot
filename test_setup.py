#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
eSIM Bot 設置測試腳本
檢查所有必要的配置和依賴是否正確設置
"""

import sys
import os
import sqlite3
from datetime import datetime

def test_python_version():
    """測試 Python 版本"""
    print("🐍 檢查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (符合要求)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (需要 3.8+)")
        return False

def test_imports():
    """測試必要的模組導入"""
    print("\n📦 檢查必要模組...")
    
    modules = [
        ('config', '配置文件'),
        ('sqlite3', 'SQLite 數據庫'),
        ('json', 'JSON 處理'),
        ('datetime', '日期時間'),
        ('logging', '日誌記錄')
    ]
    
    success = True
    for module, desc in modules:
        try:
            __import__(module)
            print(f"   ✅ {desc} ({module})")
        except ImportError as e:
            print(f"   ❌ {desc} ({module}) - {e}")
            success = False
    
    return success

def test_optional_imports():
    """測試可選模組導入"""
    print("\n📦 檢查可選模組...")
    
    optional_modules = [
        ('telegram', 'Telegram Bot API'),
        ('aiohttp', 'HTTP 客戶端'),
        ('pandas', '數據分析'),
        ('matplotlib', '圖表生成'),
        ('qrcode', 'QR Code 生成'),
        ('cryptography', '加密功能'),
        ('psutil', '系統監控'),
        ('schedule', '任務調度')
    ]
    
    available = 0
    for module, desc in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {desc} ({module})")
            available += 1
        except ImportError:
            print(f"   ⚠️  {desc} ({module}) - 未安裝")
    
    print(f"\n   📊 可選模組: {available}/{len(optional_modules)} 可用")
    return available >= 1  # 至少需要 telegram 模組

def test_config():
    """測試配置文件"""
    print("\n⚙️  檢查配置文件...")
    
    try:
        import config
        
        # 檢查必要配置
        if hasattr(config, 'BOT_TOKEN'):
            if config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
                print("   ⚠️  BOT_TOKEN 尚未設置")
            else:
                print("   ✅ BOT_TOKEN 已設置")
        else:
            print("   ❌ 缺少 BOT_TOKEN 配置")
            return False
        
        if hasattr(config, 'ADMIN_IDS'):
            if config.ADMIN_IDS == [123456789]:
                print("   ⚠️  ADMIN_IDS 使用默認值")
            else:
                print("   ✅ ADMIN_IDS 已設置")
        else:
            print("   ❌ 缺少 ADMIN_IDS 配置")
            return False
        
        # 檢查可選配置
        optional_configs = [
            'DATABASE_NAME',
            'PAYMENT_METHODS',
            'SUPPORT_USERNAME',
            'SUPPORT_EMAIL'
        ]
        
        for conf in optional_configs:
            if hasattr(config, conf):
                print(f"   ✅ {conf} 已配置")
            else:
                print(f"   ⚠️  {conf} 未配置")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 無法導入配置文件: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 配置文件錯誤: {e}")
        return False

def test_database():
    """測試數據庫功能"""
    print("\n🗄️  檢查數據庫功能...")
    
    try:
        import config
        db_name = getattr(config, 'DATABASE_NAME', 'esim_store.db')
        
        # 測試數據庫連接
        conn = sqlite3.connect(':memory:')  # 使用內存數據庫測試
        c = conn.cursor()
        
        # 測試創建表
        c.execute('''CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)''')
        c.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        c.execute("SELECT * FROM test_table")
        result = c.fetchone()
        
        conn.close()
        
        if result:
            print("   ✅ 數據庫功能正常")
            return True
        else:
            print("   ❌ 數據庫測試失敗")
            return False
            
    except Exception as e:
        print(f"   ❌ 數據庫測試錯誤: {e}")
        return False

def test_file_permissions():
    """測試文件權限"""
    print("\n📁 檢查文件權限...")
    
    files_to_check = [
        'esim-telegram-bot.py',
        'config.py',
        'manage_products.py',
        'view_orders.py',
        'run.sh'
    ]
    
    success = True
    for filename in files_to_check:
        if os.path.exists(filename):
            if os.access(filename, os.R_OK):
                print(f"   ✅ {filename} 可讀")
            else:
                print(f"   ❌ {filename} 不可讀")
                success = False
        else:
            print(f"   ❌ {filename} 不存在")
            success = False
    
    # 檢查執行權限
    if os.path.exists('run.sh'):
        if os.access('run.sh', os.X_OK):
            print("   ✅ run.sh 可執行")
        else:
            print("   ⚠️  run.sh 不可執行 (運行: chmod +x run.sh)")
    
    return success

def test_directories():
    """檢查必要目錄"""
    print("\n📂 檢查目錄結構...")
    
    # 創建必要目錄
    directories = ['logs', 'backups']
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/ 目錄存在")
        else:
            try:
                os.makedirs(directory)
                print(f"   ✅ {directory}/ 目錄已創建")
            except Exception as e:
                print(f"   ❌ 無法創建 {directory}/ 目錄: {e}")
                return False
    
    return True

def main():
    """主測試函數"""
    print("🔍 eSIM Telegram Bot 設置檢查")
    print("=" * 50)
    
    tests = [
        ("Python 版本", test_python_version),
        ("基本模組", test_imports),
        ("可選模組", test_optional_imports),
        ("配置文件", test_config),
        ("數據庫功能", test_database),
        ("文件權限", test_file_permissions),
        ("目錄結構", test_directories)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ 測試 {test_name} 時發生錯誤: {e}")
            results.append((test_name, False))
    
    # 總結
    print("\n" + "=" * 50)
    print("📋 測試結果總結:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 總計: {passed}/{len(results)} 項測試通過")
    
    if passed == len(results):
        print("\n🎉 所有測試通過！系統已準備就緒。")
        print("\n下一步:")
        print("1. 設置您的 Bot Token 在 config.py 中")
        print("2. 設置您的 Telegram ID 在 ADMIN_IDS 中")
        print("3. 運行: ./run.sh")
    elif passed >= len(results) - 2:
        print("\n⚠️  大部分測試通過，系統基本可用。")
        print("請解決失敗的測試項目以獲得最佳體驗。")
    else:
        print("\n❌ 多項測試失敗，請解決問題後重新測試。")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 