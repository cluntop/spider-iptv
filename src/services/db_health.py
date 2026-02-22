import logging
import time
import os
import sqlite3
from datetime import datetime
from threading import Thread
from src.core.database import get_db
from src.config.config import config

class DatabaseHealthChecker:
    def __init__(self):
        self.db = get_db()
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.health_status = {
            'last_check': None,
            'connection': True,
            'integrity': True,
            'size': 0,
            'indexes': True,
            'optimization': True,
            'status': 'healthy'
        }
    
    def start(self):
        """启动数据库健康检查"""
        self.running = True
        self.logger.info("数据库健康检查启动")
        
        # 启动健康检查线程
        health_thread = Thread(target=self._health_check_loop)
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
        connection_status = self._check_connection()
        if connection_status:
            self.logger.info("数据库连接正常")
        else:
            self.logger.warning("数据库连接异常")
        
        # 检查数据库完整性
        integrity_status = self._check_integrity()
        if integrity_status:
            self.logger.info("数据库完整性正常")
        else:
            self.logger.warning("数据库完整性检查失败")
        
        # 检查数据库大小
        size = self._check_database_size()
        if size:
            self.logger.info(f"数据库大小: {size:.2f} MB")
            # 检查数据库大小是否超过阈值
            if size > 100:  # 100MB阈值
                self.logger.warning(f"数据库大小超过阈值: {size:.2f} MB")
        
        # 检查索引状态
        indexes_status = self._check_indexes()
        if indexes_status:
            self.logger.info("数据库索引状态正常")
        else:
            self.logger.warning("数据库索引检查失败")
        
        # 检查表统计信息
        table_stats = self._check_table_stats()
        if table_stats:
            for table, count in table_stats.items():
                self.logger.debug(f"表 {table} 记录数: {count}")
        
        # 执行数据库优化
        optimization_status = self._optimize_database()
        if optimization_status:
            self.logger.info("数据库优化完成")
        else:
            self.logger.warning("数据库优化失败")
        
        # 更新健康状态
        self._update_health_status(connection_status, integrity_status, size, indexes_status, optimization_status)
        
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
                else:
                    self.logger.debug(f"表 {table} 有 {len(result)} 个索引")
            return True
        except Exception as e:
            self.logger.error(f"检查数据库索引失败: {e}")
            return False
    
    def _check_table_stats(self):
        """检查表统计信息"""
        try:
            tables = ['iptv_channels', 'iptv_hotels', 'iptv_multicast', 'iptv_udpxy', 'iptv_category']
            stats = {}
            for table in tables:
                try:
                    result = self.db.fetchone(f"SELECT COUNT(*) FROM {table}")
                    if result:
                        stats[table] = result[0]
                except Exception as e:
                    self.logger.debug(f"检查表 {table} 统计信息失败: {e}")
            return stats
        except Exception as e:
            self.logger.error(f"检查表统计信息失败: {e}")
            return None
    
    def _optimize_database(self):
        """优化数据库"""
        try:
            # 执行VACUUM操作
            self.db.execute("VACUUM")
            # 分析数据库以更新统计信息
            self.db.execute("ANALYZE")
            # 优化连接缓存
            self.db.execute("PRAGMA optimize")
            return True
        except Exception as e:
            self.logger.error(f"优化数据库失败: {e}")
            return False
    
    def _update_health_status(self, connection, integrity, size, indexes, optimization):
        """更新健康状态"""
        self.health_status['last_check'] = datetime.now()
        self.health_status['connection'] = connection
        self.health_status['integrity'] = integrity
        self.health_status['size'] = size
        self.health_status['indexes'] = indexes
        self.health_status['optimization'] = optimization
        
        # 确定整体状态
        if not connection:
            self.health_status['status'] = 'critical'
        elif not integrity:
            self.health_status['status'] = 'critical'
        elif size > 100:
            self.health_status['status'] = 'warning'
        elif not indexes:
            self.health_status['status'] = 'warning'
        elif not optimization:
            self.health_status['status'] = 'warning'
        else:
            self.health_status['status'] = 'healthy'
    
    def repair_database(self):
        """修复数据库"""
        self.logger.info("开始数据库修复")
        
        try:
            # 尝试重建数据库
            self.logger.warning("执行数据库重建操作")
            
            # 1. 执行完整性检查
            integrity_result = self.db.fetchone("PRAGMA integrity_check")
            if integrity_result and integrity_result[0] != "ok":
                self.logger.warning(f"数据库完整性检查失败: {integrity_result[0]}")
                
                # 2. 尝试执行REINDEX
                self.logger.info("执行REINDEX操作")
                self.db.execute("REINDEX")
                
                # 3. 再次执行完整性检查
                integrity_result = self.db.fetchone("PRAGMA integrity_check")
                if integrity_result and integrity_result[0] == "ok":
                    self.logger.info("数据库修复成功")
                else:
                    self.logger.error(f"数据库修复失败: {integrity_result[0]}")
                    return False
            
            # 4. 执行VACUUM
            self.db.execute("VACUUM")
            self.logger.info("数据库修复完成")
            return True
        except Exception as e:
            self.logger.error(f"修复数据库失败: {e}")
            return False
    
    def get_health_status(self):
        """获取健康状态"""
        return self.health_status
    
    def get_health_summary(self):
        """获取健康状态摘要"""
        status = self.health_status
        summary = {
            'status': status['status'],
            'last_check': status['last_check'],
            'size_mb': round(status['size'], 2),
            'details': {
                'connection': 'ok' if status['connection'] else 'error',
                'integrity': 'ok' if status['integrity'] else 'error',
                'indexes': 'ok' if status['indexes'] else 'warning',
                'optimization': 'ok' if status['optimization'] else 'warning'
            }
        }
        return summary