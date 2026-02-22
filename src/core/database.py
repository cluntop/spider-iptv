import sqlite3
import os
import logging
import time
from datetime import datetime
from src.config.config import config

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or config.get('database.path', 'data/iptv.db')
        self.logger = logging.getLogger(__name__)
        self._ensure_db_exists()
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 5  # 秒
    
    def _ensure_db_exists(self):
        """确保数据库文件存在并初始化表结构"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                self.logger.info(f"创建数据库目录: {db_dir}")
            except Exception as e:
                self.logger.error(f"创建数据库目录失败: {e}")
                raise
        
        retries = 0
        while retries < self.max_retries:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("PRAGMA foreign_keys = ON")
                    conn.execute("PRAGMA journal_mode = WAL")
                    conn.execute("PRAGMA synchronous = NORMAL")
                    self._create_tables(conn)
                    self.logger.info(f"数据库初始化成功: {self.db_path}")
                    return
            except sqlite3.Error as e:
                retries += 1
                self.logger.error(f"数据库初始化失败 (尝试 {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    self.logger.info(f"{self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.critical(f"数据库初始化失败，已达到最大重试次数")
                    raise
            except Exception as e:
                self.logger.error(f"数据库初始化异常: {e}")
                raise
    
    def _create_tables(self, conn):
        """创建数据库表结构"""
        cursor = conn.cursor()
        
        # 创建频道分类表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS iptv_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            psw TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            enable INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建频道表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS iptv_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            type TEXT,
            width INTEGER,
            height INTEGER,
            frame REAL,
            speed REAL DEFAULT 0.0,
            sign INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建酒店源表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS iptv_hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            port TEXT NOT NULL,
            name TEXT,
            count INTEGER DEFAULT 0,
            status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建组播表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS iptv_multicast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            province TEXT,
            isp TEXT,
            path TEXT,
            city TEXT,
            udpxy TEXT,
            lines INTEGER DEFAULT 0,
            status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建udpxy代理表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS iptv_udpxy (
            id TEXT PRIMARY KEY,
            mid INTEGER,
            mcast TEXT,
            city TEXT,
            ip TEXT,
            port INTEGER,
            actv INTEGER DEFAULT 0,
            status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mid) REFERENCES iptv_multicast (id)
        )
        ''')
        
        # 创建索引以提高查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_channels_name ON iptv_channels (name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_channels_sign ON iptv_channels (sign)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hotels_ip ON iptv_hotels (ip)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hotels_status ON iptv_hotels (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_multicast_isp ON iptv_multicast (isp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_udpxy_mid ON iptv_udpxy (mid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_udpxy_status ON iptv_udpxy (status)')
        
        conn.commit()
    
    def get_connection(self):
        """获取数据库连接"""
        retries = 0
        while retries < self.max_retries:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row  # 启用字典式游标
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA busy_timeout = 30000")  # 30秒忙等待
                return conn
            except sqlite3.Error as e:
                retries += 1
                self.logger.error(f"获取数据库连接失败 (尝试 {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    self.logger.info(f"{self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.critical(f"获取数据库连接失败，已达到最大重试次数")
                    raise
            except Exception as e:
                self.logger.error(f"获取数据库连接异常: {e}")
                raise
    
    def execute(self, query, params=()):
        """执行SQL查询"""
        retries = 0
        while retries < self.max_retries:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor
            except sqlite3.Error as e:
                retries += 1
                self.logger.error(f"SQL执行失败 (尝试 {retries}/{self.max_retries}): {query}, {params}, {e}")
                if retries < self.max_retries and 'database is locked' in str(e):
                    self.logger.info(f"{self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"SQL执行异常: {query}, {params}, {e}")
                raise
    
    def executemany(self, query, params_list):
        """批量执行SQL查询"""
        retries = 0
        while retries < self.max_retries:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.executemany(query, params_list)
                    conn.commit()
                    return cursor
            except sqlite3.Error as e:
                retries += 1
                self.logger.error(f"批量SQL执行失败 (尝试 {retries}/{self.max_retries}): {query}, {e}")
                if retries < self.max_retries and 'database is locked' in str(e):
                    self.logger.info(f"{self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"批量SQL执行异常: {query}, {e}")
                raise
    
    def fetchall(self, query, params=()):
        """执行查询并返回所有结果"""
        retries = 0
        while retries < self.max_retries:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    return cursor.fetchall()
            except sqlite3.Error as e:
                retries += 1
                self.logger.error(f"查询执行失败 (尝试 {retries}/{self.max_retries}): {query}, {params}, {e}")
                if retries < self.max_retries:
                    self.logger.info(f"{self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"查询执行异常: {query}, {params}, {e}")
                raise
    
    def fetchone(self, query, params=()):
        """执行查询并返回第一条结果"""
        retries = 0
        while retries < self.max_retries:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    return cursor.fetchone()
            except sqlite3.Error as e:
                retries += 1
                self.logger.error(f"查询执行失败 (尝试 {retries}/{self.max_retries}): {query}, {params}, {e}")
                if retries < self.max_retries:
                    self.logger.info(f"{self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"查询执行异常: {query}, {params}, {e}")
                raise
    
    def close(self):
        """关闭数据库连接"""
        # SQLite连接在with语句结束时自动关闭
        pass

# 全局数据库管理器实例
db_manager = None

def get_db():
    """获取数据库管理器实例"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager