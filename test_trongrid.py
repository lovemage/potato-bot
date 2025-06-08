#!/usr/bin/env python3
"""
TronGrid API 測試腳本
測試 API 連接和 USDT 交易查詢功能
"""

import requests
import config
import json

def test_trongrid_connection():
    """測試 TronGrid API 連接"""
    print("🔗 測試 TronGrid API 連接...")
    
    try:
        url = "https://api.trongrid.io/wallet/getnowblock"
        headers = {
            'TRON-PRO-API-KEY': config.TRONGRID_API_KEY
        }
        
        response = requests.post(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            block_number = data.get('block_header', {}).get('raw_data', {}).get('number', 0)
            print(f"✅ API 連接成功！當前區塊高度: {block_number}")
            return True
        else:
            print(f"❌ API 連接失敗！狀態碼: {response.status_code}")
            print(f"響應: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API 連接異常: {e}")
        return False

def test_usdt_address_query():
    """測試 USDT 地址查詢"""
    print(f"\n💰 測試 USDT 地址查詢...")
    print(f"地址: {config.USDT_ADDRESS}")
    
    try:
        url = f"https://api.trongrid.io/v1/accounts/{config.USDT_ADDRESS}/transactions/trc20"
        headers = {
            'TRON-PRO-API-KEY': config.TRONGRID_API_KEY
        }
        params = {
            'limit': 5,
            'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'  # USDT TRC20合約地址
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('data', [])
            
            print(f"✅ 查詢成功！找到 {len(transactions)} 筆交易")
            
            if transactions:
                print("\n📋 最近的交易:")
                for i, tx in enumerate(transactions[:3], 1):
                    amount = float(tx['value']) / 1000000  # USDT有6位小數
                    tx_type = "接收" if tx['to'] == config.USDT_ADDRESS else "發送"
                    print(f"  {i}. {tx_type} ${amount:.2f} USDT")
                    print(f"     TXID: {tx['transaction_id']}")
                    print(f"     時間: {tx['block_timestamp']}")
                    print()
            else:
                print("📝 該地址暫無 USDT 交易記錄")
                
            return True
        else:
            print(f"❌ 查詢失敗！狀態碼: {response.status_code}")
            print(f"響應: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 查詢異常: {e}")
        return False

def test_account_info():
    """測試帳戶信息查詢"""
    print(f"\n📊 測試帳戶信息查詢...")
    
    try:
        url = f"https://api.trongrid.io/v1/accounts/{config.USDT_ADDRESS}"
        headers = {
            'TRON-PRO-API-KEY': config.TRONGRID_API_KEY
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            account_data = data.get('data', [])
            
            if account_data:
                account = account_data[0]
                balance = account.get('balance', 0) / 1000000  # TRX餘額
                print(f"✅ 帳戶查詢成功！")
                print(f"   TRX 餘額: {balance:.6f} TRX")
                print(f"   地址類型: {account.get('address_tag', 'N/A')}")
                
                # 查詢 USDT 餘額
                trc20_balances = account.get('trc20', [])
                for token in trc20_balances:
                    if token.get('contract_address') == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t':
                        usdt_balance = float(token.get('balance', 0)) / 1000000
                        print(f"   USDT 餘額: {usdt_balance:.6f} USDT")
                        break
                else:
                    print("   USDT 餘額: 0.000000 USDT")
                    
            else:
                print("❌ 帳戶不存在或無數據")
                
            return True
        else:
            print(f"❌ 查詢失敗！狀態碼: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 查詢異常: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 TronGrid API 測試開始")
    print("=" * 50)
    print(f"API Key: {config.TRONGRID_API_KEY[:10]}...{config.TRONGRID_API_KEY[-10:]}")
    print(f"USDT 地址: {config.USDT_ADDRESS}")
    print("=" * 50)
    
    # 測試 API 連接
    if not test_trongrid_connection():
        print("\n❌ API 連接測試失敗，請檢查 API Key 和網絡連接")
        return
    
    # 測試 USDT 地址查詢
    test_usdt_address_query()
    
    # 測試帳戶信息
    test_account_info()
    
    print("\n" + "=" * 50)
    print("🎉 TronGrid API 測試完成！")
    print("\n💡 提示:")
    print("   - 如果查詢成功，說明 API 配置正確")
    print("   - 如果沒有交易記錄，可以先發送一筆小額 USDT 測試")
    print("   - 付款監控功能將自動檢測新的 USDT 交易")

if __name__ == "__main__":
    main() 