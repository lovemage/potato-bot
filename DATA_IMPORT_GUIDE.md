# 📊 數據導入和管理指南

## 🎯 概述

本系統支持兩種類型的卡片數據：
- **🔒 全資料卡片** - 包含完整個人信息的卡片數據
- **📊 裸庫卡片** - 僅包含純信用卡信息的數據

## 📁 數據格式

### 原始數據文件格式
數據文件應包含兩個部分，用特定標記分隔：

```
🔒 全资料 (包含个人信息)
============================================================

【個人信息或國家名稱】
----------------------------------------
卡號 到期日期 安全碼 國家/個人信息

📊 单纯数据 (仅信用卡信息)
============================================================

【國家名稱】
----------------------------------------
卡號 到期日期 安全碼 國家
```

### 示例數據格式

**全資料示例：**
```
【Anna Hwang|1, Jeongjail-ro, Bundang-gu, Seongnam-si, Gyeonggi-do, Republic of Korea|Gyeonggi do|Gyeonggi do|13616|】
----------------------------------------
4658877542073349 08/27 769 Anna Hwang|1, Jeongjail-ro, Bundang-gu, Seongnam-si, Gyeonggi-do, Republic of Korea|Gyeonggi do|Gyeonggi do|13616|

【HONG KONG】
----------------------------------------
4480602740300987 01/28 098 HONG KONG
4480607237191252 01/29 165 HONG KONG
```

**裸庫示例：**
```
【USA】
----------------------------------------
371500837215003 04/29 6418 USA
379382534811000 07/26 9097 USA

【SINGAPORE】
----------------------------------------
5523527021610612 01/26 432 SINGAPORE
4096362016190325 01/27 622 SINGAPORE
```

## 🚀 數據導入

### 1. 準備數據文件
將數據文件放置在 `data/` 目錄下，命名為 `organized_final.txt`

### 2. 運行導入工具
```bash
python import_data.py
```

### 3. 導入結果
- 系統會自動創建兩個數據表：
  - `full_data` - 存儲全資料卡片
  - `cards` - 存儲裸庫卡片
- 顯示導入統計信息
- 自動設置價格（可後續調整）

## 🛠️ 數據管理

### 查看數據統計
```bash
python quick_view.py
```

### 完整管理工具
```bash
python manage_imported_data.py
```

管理工具功能：
1. **📊 顯示統計信息** - 查看總體數據統計
2. **🌍 顯示國家分佈** - 按國家查看卡片分佈
3. **💳 查看特定國家卡片** - 查看特定國家的卡片詳情
4. **🔍 搜索卡片** - 按關鍵字搜索卡片
5. **✏️ 更新卡片狀態** - 修改卡片狀態（available/sold/reserved）
6. **💰 更新卡片價格** - 調整卡片價格
7. **🗑️ 刪除卡片** - 刪除指定卡片
8. **📤 導出卡片數據** - 導出卡片數據到文件

## 💰 價格設置

系統會根據國家自動設置價格：

### 全資料卡片價格（基礎價格 + $5.00）
- USA/UNITED STATES: $17.00
- KOREA: $13.00
- JAPAN: $15.00
- SINGAPORE: $14.00
- HONG KONG: $16.00
- PHILIPPINES: $12.00
- 其他國家: $15.00

### 裸庫卡片價格
- USA/UNITED STATES: $12.00
- KOREA: $8.00
- JAPAN: $10.00
- SINGAPORE: $9.00
- HONG KONG: $11.00
- PHILIPPINES: $7.00
- EMPCheck.Co: $5.00
- [CHECKER0.ME]: $5.00
- Live: $6.00
- 其他國家: $10.00

## 📊 當前數據統計

根據最新導入的數據：

### 🔒 全資料卡片 (196張)
- KOREA: 80 張
- USA: 57 張
- HONG KONG: 34 張
- JAPAN: 8 張
- SINGAPORE: 6 張
- 其他個人信息: 11 張

### 📊 裸庫卡片 (86張)
- SINGAPORE: 60 張
- EMPCheck.Co: 7 張
- [CHECKER0.ME]: 6 張
- USA: 5 張
- PHILIPPINES: 3 張
- KOREA: 3 張
- Live: 2 張

**總計：282 張卡片**

## 🔧 數據庫結構

### full_data 表（全資料）
```sql
CREATE TABLE full_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_number TEXT UNIQUE NOT NULL,
    expiry_date TEXT NOT NULL,
    security_code TEXT NOT NULL,
    country TEXT NOT NULL,
    personal_info TEXT,
    price REAL DEFAULT 15.0,
    status TEXT DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### cards 表（裸庫）
```sql
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_number TEXT UNIQUE NOT NULL,
    expiry_date TEXT NOT NULL,
    security_code TEXT NOT NULL,
    country TEXT NOT NULL,
    price REAL DEFAULT 10.0,
    status TEXT DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚨 注意事項

1. **數據驗證**：導入時會驗證卡號、到期日期和安全碼格式
2. **重複處理**：使用 `INSERT OR IGNORE` 避免重複導入
3. **狀態管理**：卡片狀態包括 `available`、`sold`、`reserved`
4. **備份建議**：定期備份數據庫文件 `esim_bot.db`
5. **價格調整**：可通過管理工具隨時調整價格

## 📞 技術支持

如遇到問題，請檢查：
1. 數據文件格式是否正確
2. 數據庫文件權限
3. Python 環境和依賴包
4. 日誌輸出信息

## 🔄 更新數據

要添加新的卡片數據：
1. 準備新的數據文件
2. 運行導入工具
3. 系統會自動跳過重複的卡片
4. 查看導入統計確認結果 