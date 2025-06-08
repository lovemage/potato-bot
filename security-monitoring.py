# security_module.py - 安全模組

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
import re
from typing import Dict, List, Optional

class SecurityModule:
    """處理所有安全相關功能"""
    
    def __init__(self):
        self.rate_limits = {}  # 速率限制記錄
        self.blocked_users = set()  # 被封鎖的用戶
        self.failed_attempts = {}  # 失敗嘗試記錄
        
    def rate_limiter(self, max_calls: int = 10, window: int = 60):
        """速率限制裝飾器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(update, context, *args, **kwargs):
                user_id = update.effective_user.id
                current_time = time.time()
                
                # 初始化用戶記錄
                if user_id not in self.rate_limits:
                    self.rate_limits[user_id] = []
                
                # 清理過期記錄
                self.rate_limits[user_id] = [
                    timestamp for timestamp in self.rate_limits[user_id]
                    if current_time - timestamp < window
                ]
                
                # 檢查速率限制
                if len(self.rate_limits[user_id]) >= max_calls:
                    await update.message.reply_text(
                        "⚠️ 請求過於頻繁，請稍後再試。"
                    )
                    return
                
                # 記錄此次調用
                self.rate_limits[user_id].append(current_time)
                
                # 執行原函數
                return await func(update, context, *args, **kwargs)
            
            return wrapper
        return decorator
    
    def check_user_blocked(self, user_id: int) -> bool:
        """檢查用戶是否被封鎖"""
        return user_id in self.blocked_users
    
    def block_user(self, user_id: int, reason: str = ""):
        """封鎖用戶"""
        self.blocked_users.add(user_id)
        # 記錄封鎖原因和時間
        with open('blocked_users.log', 'a') as f:
            f.write(f"{datetime.now()}: User {user_id} blocked. Reason: {reason}\n")
    
    def unblock_user(self, user_id: int):
        """解封用戶"""
        self.blocked_users.discard(user_id)
    
    def validate_input(self, text: str, input_type: str) -> bool:
        """驗證用戶輸入"""
        validators = {
            'email': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            'phone': r'^\+?[1-9]\d{1,14}$',
            'transaction_hash': r'^[a-fA-F0-9]{64}$',
            'usdt_address': r'^T[a-zA-Z0-9]{33}$'  # TRC20 地址格式
        }
        
        pattern = validators.get(input_type)
        if pattern:
            return bool(re.match(pattern, text))
        
        return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """生成安全令牌"""
        return secrets.token_urlsafe(length)
    
    def verify_payment_signature(self, data: Dict, signature: str, secret: str) -> bool:
        """驗證支付回調簽名"""
        # 根據支付平台的規則生成簽名
        message = ''.join([str(data[key]) for key in sorted(data.keys())])
        expected_signature = hashlib.sha256(
            f"{message}{secret}".encode()
        ).hexdigest()
        
        return secrets.compare_digest(signature, expected_signature)
    
    async def anti_fraud_check(self, user_id: int, order_data: Dict) -> Dict:
        """反欺詐檢查"""
        risk_score = 0
        risk_factors = []
        
        # 檢查新用戶
        if order_data.get('is_new_user'):
            risk_score += 20
            risk_factors.append("新用戶")
        
        # 檢查訂單金額
        if order_data.get('amount', 0) > 100:
            risk_score += 30
            risk_factors.append("高額訂單")
        
        # 檢查購買頻率
        recent_orders = order_data.get('recent_orders_count', 0)
        if recent_orders > 5:
            risk_score += 40
            risk_factors.append("頻繁購買")
        
        # 檢查失敗支付記錄
        failed_payments = self.failed_attempts.get(user_id, 0)
        if failed_payments > 3:
            risk_score += 50
            risk_factors.append("多次支付失敗")
        
        return {
            'risk_score': risk_score,
            'risk_level': 'high' if risk_score > 60 else 'medium' if risk_score > 30 else 'low',
            'risk_factors': risk_factors,
            'action': 'block' if risk_score > 80 else 'review' if risk_score > 60 else 'pass'
        }
    
    def encrypt_sensitive_data(self, data: str, key: str) -> str:
        """加密敏感數據"""
        # 使用簡單的 XOR 加密示例，實際應使用更強的加密算法
        # 建議使用 cryptography 庫的 Fernet
        from cryptography.fernet import Fernet
        
        if not hasattr(self, '_fernet'):
            self._fernet = Fernet(Fernet.generate_key())
        
        return self._fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str, key: str) -> str:
        """解密敏感數據"""
        if hasattr(self, '_fernet'):
            return self._fernet.decrypt(encrypted_data.encode()).decode()
        return ""

# monitoring_system.py - 監控系統

import psutil
import asyncio
from collections import deque
from datetime import datetime, timedelta

class MonitoringSystem:
    """系統監控模組"""
    
    def __init__(self, alert_callback=None):
        self.metrics = {
            'response_times': deque(maxlen=1000),
            'error_count': 0,
            'success_count': 0,
            'active_users': set(),
            'daily_orders': deque(maxlen=30)
        }
        self.alert_callback = alert_callback
        self.alert_thresholds = {
            'response_time': 3.0,  # 秒
            'error_rate': 0.1,  # 10%
            'cpu_usage': 80,  # 百分比
            'memory_usage': 80  # 百分比
        }
    
    async def log_request(self, user_id: int, command: str, response_time: float, success: bool):
        """記錄請求"""
        self.metrics['response_times'].append(response_time)
        self.metrics['active_users'].add(user_id)
        
        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['error_count'] += 1
        
        # 檢查是否需要發送警報
        await self._check_alerts()
    
    async def _check_alerts(self):
        """檢查並發送警報"""
        # 檢查響應時間
        if self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            if avg_response_time > self.alert_thresholds['response_time']:
                await self._send_alert(f"高響應時間警報: {avg_response_time:.2f}秒")
        
        # 檢查錯誤率
        total_requests = self.metrics['success_count'] + self.metrics['error_count']
        if total_requests > 100:
            error_rate = self.metrics['error_count'] / total_requests
            if error_rate > self.alert_thresholds['error_rate']:
                await self._send_alert(f"高錯誤率警報: {error_rate:.2%}")
    
    async def _send_alert(self, message: str):
        """發送警報"""
        if self.alert_callback:
            await self.alert_callback(message)
    
    def get_system_stats(self) -> Dict:
        """獲取系統統計信息"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available / (1024 ** 3),  # GB
            'disk_usage': disk.percent,
            'disk_free': disk.free / (1024 ** 3),  # GB
            'active_users': len(self.metrics['active_users']),
            'total_requests': self.metrics['success_count'] + self.metrics['error_count'],
            'error_rate': self.metrics['error_count'] / max(1, self.metrics['success_count'] + self.metrics['error_count'])
        }
    
    async def generate_health_report(self) -> str:
        """生成健康報告"""
        stats = self.get_system_stats()
        
        report = f"""
📊 系統健康報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🖥️ 系統資源:
• CPU 使用率: {stats['cpu_usage']:.1f}%
• 內存使用率: {stats['memory_usage']:.1f}%
• 可用內存: {stats['memory_available']:.1f} GB
• 硬盤使用率: {stats['disk_usage']:.1f}%
• 可用空間: {stats['disk_free']:.1f} GB

📈 運行統計:
• 活躍用戶: {stats['active_users']}
• 總請求數: {stats['total_requests']}
• 錯誤率: {stats['error_rate']:.2%}

狀態: {'⚠️ 需要關注' if any([
    stats['cpu_usage'] > 80,
    stats['memory_usage'] > 80,
    stats['error_rate'] > 0.1
]) else '✅ 運行正常'}
        """
        
        return report
    
    async def cleanup_old_data(self, days: int = 30):
        """清理舊數據"""
        # 實現數據清理邏輯
        pass

# backup_restore.py - 備份與恢復

import shutil
import zipfile
from pathlib import Path

class BackupRestore:
    """備份與恢復系統"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, db_path: str, include_logs: bool = True) -> str:
        """創建備份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        # 備份數據庫
        shutil.copy2(db_path, backup_path / "database.db")
        
        # 備份日誌文件
        if include_logs:
            logs_dir = backup_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            for log_file in Path(".").glob("*.log"):
                shutil.copy2(log_file, logs_dir)
        
        # 創建壓縮包
        zip_path = f"{backup_path}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in backup_path.rglob('*'):
                if file.is_file():
                    zipf.write(file, file.relative_to(backup_path))
        
        # 刪除臨時目錄
        shutil.rmtree(backup_path)
        
        return zip_path
    
    def restore_backup(self, backup_file: str, target_db_path: str) -> bool:
        """恢復備份"""
        try:
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # 提取到臨時目錄
                temp_dir = Path("temp_restore")
                zipf.extractall(temp_dir)
                
                # 恢復數據庫
                db_backup = temp_dir / "database.db"
                if db_backup.exists():
                    shutil.copy2(db_backup, target_db_path)
                
                # 清理臨時目錄
                shutil.rmtree(temp_dir)
                
                return True
        except Exception as e:
            print(f"恢復失敗: {e}")
            return False
    
    def auto_backup_scheduler(self, db_path: str, interval_hours: int = 24):
        """自動備份調度器"""
        import schedule
        
        def backup_job():
            try:
                backup_file = self.create_backup(db_path)
                print(f"自動備份完成: {backup_file}")
                
                # 清理舊備份（保留最近7個）
                self._cleanup_old_backups(keep_count=7)
            except Exception as e:
                print(f"自動備份失敗: {e}")
        
        schedule.every(interval_hours).hours.do(backup_job)
    
    def _cleanup_old_backups(self, keep_count: int = 7):
        """清理舊備份"""
        backups = sorted(self.backup_dir.glob("backup_*.zip"))
        
        if len(backups) > keep_count:
            for backup in backups[:-keep_count]:
                backup.unlink()

# audit_logger.py - 審計日誌

class AuditLogger:
    """審計日誌系統"""
    
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        
    def log_event(self, event_type: str, user_id: int, details: Dict):
        """記錄審計事件"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def log_order(self, user_id: int, order_id: int, product_id: int, amount: float):
        """記錄訂單事件"""
        self.log_event('order_created', user_id, {
            'order_id': order_id,
            'product_id': product_id,
            'amount': amount
        })
    
    def log_payment(self, user_id: int, order_id: int, method: str, status: str):
        """記錄支付事件"""
        self.log_event('payment', user_id, {
            'order_id': order_id,
            'method': method,
            'status': status
        })
    
    def log_admin_action(self, admin_id: int, action: str, target: str):
        """記錄管理員操作"""
        self.log_event('admin_action', admin_id, {
            'action': action,
            'target': target
        })
    
    def get_user_history(self, user_id: int) -> List[Dict]:
        """獲取用戶歷史記錄"""
        history = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                event = json.loads(line.strip())
                if event['user_id'] == user_id:
                    history.append(event)
        
        return history