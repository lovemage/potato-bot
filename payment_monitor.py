#!/usr/bin/env python3
"""
USDT 付款監控腳本
定期檢查用戶充值並自動到賬
"""

import time
import asyncio
import logging
from datetime import datetime
from wallet_manager import wallet_manager
import config

# 設置日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PaymentMonitor:
    def __init__(self):
        self.running = False
        self.check_interval = 30  # 30秒檢查一次
    
    async def start_monitoring(self):
        """開始監控付款"""
        self.running = True
        logger.info("🔍 付款監控已啟動")
        
        while self.running:
            try:
                # 處理待確認的充值
                wallet_manager.process_pending_deposits()
                
                # 等待下次檢查
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"監控過程中發生錯誤: {e}")
                await asyncio.sleep(60)  # 錯誤時等待1分鐘
    
    def stop_monitoring(self):
        """停止監控"""
        self.running = False
        logger.info("⏹️ 付款監控已停止")

async def main():
    """主函數"""
    monitor = PaymentMonitor()
    
    try:
        logger.info("🚀 啟動 USDT 付款監控系統")
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("📱 收到停止信號")
        monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"監控系統錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 