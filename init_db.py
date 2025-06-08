#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
數據庫初始化腳本
創建數據庫表並插入示例數據
"""

import sqlite3
import config

def init_db():
    conn = sqlite3.connect(config.DATABASE_NAME)
    c = conn.cursor()
    
    # 創建產品表（卡片）
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_number TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        security_code TEXT NOT NULL,
        country TEXT NOT NULL,
        price REAL NOT NULL,
        status TEXT DEFAULT 'available',
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 創建訂單表
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        card_id INTEGER,
        card_number TEXT,
        country TEXT,
        price REAL,
        payment_method TEXT DEFAULT 'usdt',
        status TEXT DEFAULT 'pending',
        order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (card_id) REFERENCES products (id)
    )''')
    
    # 創建用戶錢包表
    c.execute('''CREATE TABLE IF NOT EXISTS user_wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        balance REAL DEFAULT 0.0,
        total_deposited REAL DEFAULT 0.0,
        total_spent REAL DEFAULT 0.0,
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 創建交易記錄表
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        transaction_type TEXT NOT NULL,  -- 'deposit', 'purchase', 'refund'
        amount REAL NOT NULL,
        balance_before REAL NOT NULL,
        balance_after REAL NOT NULL,
        description TEXT,
        txid TEXT,  -- USDT交易哈希
        order_id INTEGER,
        status TEXT DEFAULT 'completed',
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )''')
    
    # 創建充值記錄表
    c.execute('''CREATE TABLE IF NOT EXISTS deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        amount REAL NOT NULL,
        usdt_address TEXT NOT NULL,
        txid TEXT UNIQUE,
        status TEXT DEFAULT 'pending',  -- 'pending', 'confirmed', 'failed'
        confirmations INTEGER DEFAULT 0,
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        confirmed_time TIMESTAMP
    )''')
    
    # 創建USDT地址池表
    c.execute('''CREATE TABLE IF NOT EXISTS usdt_addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT UNIQUE NOT NULL,
        private_key TEXT,  -- 加密存儲
        is_used BOOLEAN DEFAULT FALSE,
        user_id INTEGER,
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 插入示例卡片數據
    sample_cards = [
        # 美國卡片 (5張)
        ('371500837215003', '04/29', '6418', 'UNITED STATES', 15.00),
        ('379382534811000', '07/26', '9097', 'UNITED STATES', 12.00),
        ('379382739081003', '11/26', '4630', 'UNITED STATES', 15.00),
        ('371287709643005', '12/27', '3406', 'UNITED STATES', 10.00),
        ('376750088103003', '10/26', '6001', 'UNITED STATES', 15.00),
        
        # 日本卡片 (5張)
        ('4532123456789012', '08/27', '123', 'JAPAN', 12.00),
        ('4532987654321098', '09/28', '456', 'JAPAN', 10.00),
        ('4532111222333444', '10/29', '789', 'JAPAN', 12.00),
        ('4532555666777888', '11/30', '012', 'JAPAN', 8.00),
        ('4532999000111222', '12/31', '345', 'JAPAN', 12.00),
        
        # 韓國卡片 (4張)
        ('5555123456789012', '06/28', '678', 'SOUTH KOREA', 10.00),
        ('5555987654321098', '07/29', '901', 'SOUTH KOREA', 8.00),
        ('5555111222333444', '08/30', '234', 'SOUTH KOREA', 10.00),
        ('5555555666777888', '09/31', '567', 'SOUTH KOREA', 6.00),
        
        # 英國卡片 (2張)
        ('4000123456789012', '05/28', '890', 'UNITED KINGDOM', 15.00),
        ('4000987654321098', '06/29', '123', 'UNITED KINGDOM', 12.00),
        
        # 德國卡片 (2張)
        ('4111123456789012', '07/28', '456', 'GERMANY', 12.00),
        ('4111987654321098', '08/29', '789', 'GERMANY', 10.00),
        
        # 法國卡片 (2張)
        ('4222123456789012', '09/28', '012', 'FRANCE', 12.00),
        ('4222987654321098', '10/29', '345', 'FRANCE', 10.00),
        
        # 澳洲卡片 (2張)
        ('4333123456789012', '11/28', '678', 'AUSTRALIA', 15.00),
        ('4333987654321098', '12/29', '901', 'AUSTRALIA', 12.00),
        
        # 加拿大卡片 (2張)
        ('4444123456789012', '01/30', '234', 'CANADA', 12.00),
        ('4444987654321098', '02/31', '567', 'CANADA', 10.00),
        
        # 新加坡卡片 (1張)
        ('4555123456789012', '03/30', '890', 'SINGAPORE', 15.00),
    ]
    
    for card in sample_cards:
        c.execute("INSERT OR IGNORE INTO products (card_number, expiry_date, security_code, country, price) VALUES (?, ?, ?, ?, ?)", card)
    
    # 插入菲律賓卡片（從文件導入的）
    philippines_cards = [
        ('6250330137939695', '08/29', '507', 'PHILIPPINES', 10.00),
        ('6250330264395059', '05/29', '807', 'PHILIPPINES', 10.00),
        ('6250330136493066', '09/28', '739', 'PHILIPPINES', 10.00),
    ]
    
    for card in philippines_cards:
        c.execute("INSERT OR IGNORE INTO products (card_number, expiry_date, security_code, country, price) VALUES (?, ?, ?, ?, ?)", card)
    
    # 插入示例USDT地址（實際使用時需要真實地址）
    sample_addresses = [
        'TQn9Y2khEsLMWD2YhUKXiMcPAlK467Zffs',
        'TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7',
        'TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9',
        'TKzxg8LWyBPAaGWeFMwqHGTebp8jp4ztaP',
        'TYDzsYUEpvnYmQk7UBruoW4eWFqB2yAhEL'
    ]
    
    for addr in sample_addresses:
        c.execute("INSERT OR IGNORE INTO usdt_addresses (address) VALUES (?)", (addr,))
    
    conn.commit()
    conn.close()
    print("✅ 數據庫初始化完成，包含錢包和交易系統")

if __name__ == "__main__":
    init_db() 