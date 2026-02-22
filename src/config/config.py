import os
import json
import logging
from datetime import timedelta

class Config:
    def __init__(self):
        self.config_file = 'config.json'
        self._load_config()
        self._setup_logging()
    
    def _load_config(self):
        """加载配置文件"""
        default_config = {
            "database": {
                "path": "data/iptv.db"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/iptv.log",
                "max_bytes": 10485760,
                "backup_count": 5
            },
            "crawler": {
                "timeout": 30,
                "retry_count": 3,
                "retry_delay": 5,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "sources": [
                    {
                        "name": "iptv_im2k",
                        "url": "https://iptv.im2k.com/",
                        "enabled": True
                    },
                    {
                        "name": "m3u_ibert",
                        "url": "https://m3u.ibert.me/",
                        "enabled": True
                    }
                ]
            },
            "scheduler": {
                "download_interval": 24,  # 小时
                "check_interval": 6,  # 小时
                "cleanup_interval": 72  # 小时
            },
            "validation": {
                "timeout": 15,
                "min_speed": 1.0,
                "max_retries": 3
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                logging.error(f"加载配置文件失败: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self._save_config()
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
    
    def _setup_logging(self):
        """设置日志配置"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/iptv.log')
        max_bytes = log_config.get('max_bytes', 10485760)
        backup_count = log_config.get('backup_count', 5)
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    @property
    def database(self):
        """数据库配置"""
        return self.config.get('database', {})
    
    @property
    def logging(self):
        """日志配置"""
        return self.config.get('logging', {})
    
    @property
    def crawler(self):
        """爬虫配置"""
        return self.config.get('crawler', {})
    
    @property
    def scheduler(self):
        """调度器配置"""
        return self.config.get('scheduler', {})
    
    @property
    def validation(self):
        """验证配置"""
        return self.config.get('validation', {})
    
    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config()

# 全局配置实例
config = Config()