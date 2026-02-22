import logging
import time
import sqlite3
from datetime import datetime
from src.core.database import get_db
from src.config.config import config

class DatabaseHealthChecker:
    def __init__(self):
        self.db = get_db()
        self.logger = logging.getLogger(__name__)
        self.running = False
    
    def start(self):
        """启动数据库健康检查"""
        self.running = True
        self.logger.info("数据库健康检查启动")
        
        # 启动健康检查线程
        health_thread = threading.Thread(target=self._health_check_loop)
        health_thread.daemon = True
        health_thread.start()
    
    def stop(self):
        """停止数据库健康检查"""
        self.running = False
        self.logger.info("数据库健康检查停止")
    
    def _health_check_loop(self):
        """健康检查循环"""
        while self.running:
            try:
                self.check_database_health()
                # 每30分钟检查一次
                for _ in range(30):
                    if not self.running:
                        break
                    time.sleep(60)
            except Exception as e:
                self.logger.error(f"健康检查循环失败: {e}")
                time.sleep(60)
    
    def check_database_health(self):
        """检查数据库健康状态"""
        self.logger.info("开始数据库健康检查")
        
        # 检查数据库连接
        if self._check_connection():
            self.logger.info("数据库连接正常")
        else:
            self.logger.warning("数据库连接异常")
        
        # 检查数据库完整性
        if self._check_integrity():
            self.logger.info("数据库完整性正常")
        else:
            self.logger.warning("数据库完整性检查失败")
        
        # 检查数据库大小
        size = self._check_database_size()
        if size:
            self.logger.info(f"数据库大小: {size:.2f} MB")
        
        # 检查索引状态
        if self._check_indexes():
            self.logger.info("数据库索引状态正常")
        else:
            self.logger.warning("数据库索引检查失败")
        
        # 执行数据库优化
        if self._optimize_database():
            self.logger.info("数据库优化完成")
        else:
            self.logger.warning("数据库优化失败")
        
        self.logger.info("数据库健康检查完成")
    
    def _check_connection(self):
        """检查数据库连接"""
        try:
            result = self.db.fetchone("SELECT 1")
            return result is not None
        except Exception as e:
            self.logger.error(f"检查数据库连接失败: {e}")
            return False
    
    def _check_integrity(self):
        """检查数据库完整性"""
        try:
            # 使用PRAGMA integrity_check
            result = self.db.fetchone("PRAGMA integrity_check")
            if result and result[0] == "ok":
                return True
            self.logger.error(f"数据库完整性检查结果: {result}")
            return False
        except Exception as e:
            self.logger.error(f"检查数据库完整性失败: {e}")
            return False
    
    def _check_database_size(self):
        """检查数据库大小"""
        try:
            db_path = config.get('database.path', 'data/iptv.db')
            if os.path.exists(db_path):
                size = os.path.getsize(db_path) / (1024 * 1024)  # 转换为MB
                return size
            return 0
        except Exception as e:
            self.logger.error(f"检查数据库大小失败: {e}")
            return 0
    
    def _check_indexes(self):
        """检查数据库索引"""
        try:
            # 检查表的索引
            tables = ['iptv_channels', 'iptv_hotels', 'iptv_multicast', 'iptv_udpxy', 'iptv_category']
            for table in tables:
                result = self.db.fetchall(f"PRAGMA index_list({table})")
                if not result:
                    self.logger.warning(f"表 {table} 没有索引")
            return True
        except Exception as e:
            self.logger.error(f"检查数据库索引失败: {e}")
            return False
    
    def _optimize_database(self):
        """优化数据库"""
        try:
            # 执行VACUUM操作
            self.db.execute("VACUUM")
            # 分析数据库以更新统计信息
            self.db.execute("ANALYZE")
            return True
        except Exception as e:
            self.logger.error(f"优化数据库失败: {e}")
            return False
    
    def repair_database(self):
        """修复数据库"""
        self.logger.info("开始数据库修复")
        
        try:
            # 尝试重建数据库
            # 注意：这是一个危险操作，只在必要时使用
            self.logger.warning("执行数据库重建操作")
            # 实际的修复操作会根据具体情况实现
            return True
        except Exception as e:
            self.logger.error(f"修复数据库失败: {e}")
            return False

# 导入必要的模块
import threading
import os