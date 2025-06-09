# 🛠️ eSIM Bot 工具集

本資料夾包含 eSIM Bot 系統的各種管理和維護工具。

## 📊 數據管理工具

### `import_new_data.py`
- **功能**: 導入新的 v0.6.7 格式數據文件
- **用法**: `python3 tool/import_new_data.py`
- **說明**: 處理裸庫和全資料文件，自動分類和定價

### `clean_data.py`
- **功能**: 清理和修復數據庫中的數據
- **用法**: `python3 tool/clean_data.py`
- **說明**: 修復國家分類錯誤，標準化數據格式

### `manage_imported_data.py`
- **功能**: 全面的數據管理工具
- **用法**: `python3 tool/manage_imported_data.py`
- **功能包括**:
  - 查看統計信息
  - 搜索卡片
  - 更新狀態和價格
  - 導出數據

### `quick_view.py`
- **功能**: 快速查看數據庫統計
- **用法**: `python3 tool/quick_view.py`
- **說明**: 顯示簡潔的數據統計信息

### `check_other_data.py`
- **功能**: 檢查數據質量
- **用法**: `python3 tool/check_other_data.py`
- **說明**: 檢查分類為OTHER的數據樣本

## 🛍️ 產品管理工具

### `manage_products.py`
- **功能**: 產品管理工具
- **用法**: `python3 tool/manage_products.py`
- **功能包括**:
  - 添加/編輯/刪除產品
  - 管理產品分類
  - 設置價格和庫存

## 💰 錢包管理工具

### `wallet_admin.py`
- **功能**: 錢包管理工具
- **用法**: `python3 tool/wallet_admin.py`
- **功能包括**:
  - 查看錢包餘額
  - 管理交易記錄
  - 用戶錢包操作

## 📋 訂單管理工具

### `view_orders.py`
- **功能**: 訂單查看和管理
- **用法**: `python3 tool/view_orders.py`
- **功能包括**:
  - 查看所有訂單
  - 訂單狀態管理
  - 訂單統計分析

## 🚀 使用建議

1. **日常維護**: 定期運行 `quick_view.py` 檢查數據狀態
2. **數據導入**: 有新數據時使用 `import_new_data.py`
3. **數據清理**: 發現數據問題時使用 `clean_data.py`
4. **全面管理**: 使用 `manage_imported_data.py` 進行詳細操作

## ⚠️ 注意事項

- 所有工具都需要在項目根目錄運行
- 確保數據庫文件 `esim_bot.db` 存在
- 建議在操作前備份數據庫
- 某些操作可能需要管理員權限

---
**更新時間**: 2025-06-09  
**版本**: v1.0 