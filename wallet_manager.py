import sqlite3
import requests
import time
from datetime import datetime
import config
import logging

logger = logging.getLogger(__name__)

class WalletManager:
    def __init__(self):
        self.db_name = config.DATABASE_NAME
    
    def get_or_create_wallet(self, user_id, username):
        """獲取或創建用戶錢包"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 檢查是否已有錢包
        c.execute("SELECT * FROM user_wallets WHERE user_id = ?", (user_id,))
        wallet = c.fetchone()
        
        if not wallet:
            # 創建新錢包
            c.execute("""INSERT INTO user_wallets (user_id, username, balance) 
                         VALUES (?, ?, 0.0)""", (user_id, username))
            conn.commit()
            
            c.execute("SELECT * FROM user_wallets WHERE user_id = ?", (user_id,))
            wallet = c.fetchone()
        
        conn.close()
        return wallet
    
    def get_balance(self, user_id):
        """獲取用戶餘額"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute("SELECT balance FROM user_wallets WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        
        conn.close()
        return result[0] if result else 0.0
    
    def add_balance(self, user_id, username, amount, description="充值", txid=None):
        """增加用戶餘額"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            # 獲取當前餘額
            current_balance = self.get_balance(user_id)
            new_balance = current_balance + amount
            
            # 更新錢包餘額
            c.execute("""UPDATE user_wallets 
                         SET balance = ?, total_deposited = total_deposited + ?, updated_time = CURRENT_TIMESTAMP 
                         WHERE user_id = ?""", (new_balance, amount, user_id))
            
            # 記錄交易
            c.execute("""INSERT INTO transactions 
                         (user_id, username, transaction_type, amount, balance_before, balance_after, description, txid)
                         VALUES (?, ?, 'deposit', ?, ?, ?, ?, ?)""", 
                      (user_id, username, amount, current_balance, new_balance, description, txid))
            
            conn.commit()
            logger.info(f"用戶 {user_id} 充值 ${amount}, 餘額: ${current_balance} -> ${new_balance}")
            return True, new_balance
            
        except Exception as e:
            conn.rollback()
            logger.error(f"充值失敗: {e}")
            return False, 0
        finally:
            conn.close()
    
    def deduct_balance(self, user_id, username, amount, description="購買", order_id=None):
        """扣除用戶餘額"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            # 獲取當前餘額
            current_balance = self.get_balance(user_id)
            
            if current_balance < amount:
                return False, current_balance, "餘額不足"
            
            new_balance = current_balance - amount
            
            # 更新錢包餘額
            c.execute("""UPDATE user_wallets 
                         SET balance = ?, total_spent = total_spent + ?, updated_time = CURRENT_TIMESTAMP 
                         WHERE user_id = ?""", (new_balance, amount, user_id))
            
            # 記錄交易
            c.execute("""INSERT INTO transactions 
                         (user_id, username, transaction_type, amount, balance_before, balance_after, description, order_id)
                         VALUES (?, ?, 'purchase', ?, ?, ?, ?, ?)""", 
                      (user_id, username, amount, current_balance, new_balance, description, order_id))
            
            conn.commit()
            logger.info(f"用戶 {user_id} 消費 ${amount}, 餘額: ${current_balance} -> ${new_balance}")
            return True, new_balance, "扣款成功"
            
        except Exception as e:
            conn.rollback()
            logger.error(f"扣款失敗: {e}")
            return False, 0, f"扣款失敗: {e}"
        finally:
            conn.close()
    
    def get_transaction_history(self, user_id, limit=10):
        """獲取用戶交易記錄"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute("""SELECT transaction_type, amount, balance_after, description, created_time 
                     FROM transactions 
                     WHERE user_id = ? 
                     ORDER BY created_time DESC 
                     LIMIT ?""", (user_id, limit))
        
        transactions = c.fetchall()
        conn.close()
        return transactions
    
    def assign_usdt_address(self, user_id):
        """為用戶分配USDT充值地址"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 查找未使用的地址
        c.execute("SELECT address FROM usdt_addresses WHERE is_used = FALSE LIMIT 1")
        result = c.fetchone()
        
        if result:
            address = result[0]
            # 標記地址為已使用
            c.execute("UPDATE usdt_addresses SET is_used = TRUE, user_id = ? WHERE address = ?", 
                     (user_id, address))
            conn.commit()
            conn.close()
            return address
        else:
            conn.close()
            # 如果沒有可用地址，返回默認地址
            return config.USDT_ADDRESS
    
    def create_deposit_record(self, user_id, username, amount, address):
        """創建充值記錄"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute("""INSERT INTO deposits (user_id, username, amount, usdt_address, status)
                     VALUES (?, ?, ?, ?, 'pending')""", (user_id, username, amount, address))
        
        deposit_id = c.lastrowid
        conn.commit()
        conn.close()
        return deposit_id
    
    def check_usdt_payment(self, address, expected_amount, min_confirmations=1):
        """檢查USDT付款（使用TronGrid API）"""
        try:
            # TronGrid API查詢TRC20交易
            url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
            params = {
                'limit': 20,
                'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'  # USDT TRC20合約地址
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for tx in data.get('data', []):
                    # 檢查是否為接收交易
                    if tx['to'] == address:
                        amount = float(tx['value']) / 1000000  # USDT有6位小數
                        txid = tx['transaction_id']
                        
                        # 檢查金額是否匹配
                        if abs(amount - expected_amount) < 0.01:  # 允許0.01的誤差
                            # 檢查確認數
                            confirmations = self.get_transaction_confirmations(txid)
                            if confirmations >= min_confirmations:
                                return True, txid, amount, confirmations
                
            return False, None, 0, 0
            
        except Exception as e:
            logger.error(f"檢查USDT付款失敗: {e}")
            return False, None, 0, 0
    
    def get_transaction_confirmations(self, txid):
        """獲取交易確認數"""
        try:
            url = f"https://api.trongrid.io/wallet/gettransactionbyid"
            data = {"value": txid}
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                tx_data = response.json()
                if 'blockNumber' in tx_data:
                    # 獲取當前區塊高度
                    current_block = self.get_current_block_number()
                    tx_block = tx_data['blockNumber']
                    return max(0, current_block - tx_block)
            
            return 0
        except:
            return 0
    
    def get_current_block_number(self):
        """獲取當前區塊高度"""
        try:
            url = "https://api.trongrid.io/wallet/getnowblock"
            response = requests.post(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('block_header', {}).get('raw_data', {}).get('number', 0)
            return 0
        except:
            return 0
    
    def process_pending_deposits(self):
        """處理待確認的充值"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 獲取所有待確認的充值
        c.execute("SELECT * FROM deposits WHERE status = 'pending'")
        pending_deposits = c.fetchall()
        
        for deposit in pending_deposits:
            deposit_id, user_id, username, amount, address, txid, status, confirmations, created_time, confirmed_time = deposit
            
            # 檢查付款
            paid, found_txid, paid_amount, conf_count = self.check_usdt_payment(address, amount)
            
            if paid:
                # 更新充值記錄
                c.execute("""UPDATE deposits 
                             SET status = 'confirmed', txid = ?, confirmations = ?, confirmed_time = CURRENT_TIMESTAMP 
                             WHERE id = ?""", (found_txid, conf_count, deposit_id))
                
                # 增加用戶餘額
                success, new_balance = self.add_balance(user_id, username, paid_amount, f"USDT充值確認", found_txid)
                
                if success:
                    logger.info(f"充值確認成功: 用戶{user_id}, 金額${paid_amount}, TXID:{found_txid}")
                
        conn.commit()
        conn.close()

# 全局錢包管理器實例
wallet_manager = WalletManager() 