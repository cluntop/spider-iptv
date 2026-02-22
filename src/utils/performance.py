import psutil
import time
import logging
import functools
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.process = psutil.Process()
    
    def get_memory_usage(self):
        """获取当前内存使用情况"""
        try:
            memory_info = self.process.memory_info()
            return {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': self.process.memory_percent()
            }
        except Exception as e:
            self.logger.error(f"获取内存使用情况失败: {e}")
            return {}
    
    def get_cpu_usage(self):
        """获取当前CPU使用情况"""
        try:
            return {
                'percent': self.process.cpu_percent(interval=0.1),
                'cores': psutil.cpu_count()
            }
        except Exception as e:
            self.logger.error(f"获取CPU使用情况失败: {e}")
            return {}
    
    def monitor_function(self, func):
        """监控函数性能的装饰器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = self.get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                end_memory = self.get_memory_usage()
                execution_time = end_time - start_time
                
                memory_diff = {}
                if start_memory and end_memory:
                    memory_diff['rss'] = end_memory['rss'] - start_memory['rss']
                    memory_diff['vms'] = end_memory['vms'] - start_memory['vms']
                
                self.logger.info(f"函数性能: {func.__name__}")
                self.logger.info(f"  执行时间: {execution_time:.4f} 秒")
                if memory_diff:
                    self.logger.info(f"  内存变化: RSS {memory_diff['rss']:.2f} MB, VMS {memory_diff['vms']:.2f} MB")
                
                # 如果执行时间过长，记录警告
                if execution_time > 5:
                    self.logger.warning(f"函数执行时间过长: {func.__name__} - {execution_time:.2f} 秒")
        return wrapper
    
    def monitor_memory_usage(self, interval=5):
        """监控内存使用情况"""
        self.logger.info("开始监控内存使用情况")
        
        try:
            while True:
                memory = self.get_memory_usage()
                cpu = self.get_cpu_usage()
                
                if memory:
                    self.logger.info(f"内存使用: RSS {memory['rss']:.2f} MB ({memory['percent']:.1f}%), VMS {memory['vms']:.2f} MB")
                if cpu:
                    self.logger.info(f"CPU使用: {cpu['percent']:.1f}% ({cpu['cores']} 核心)")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("内存监控已停止")
        except Exception as e:
            self.logger.error(f"内存监控失败: {e}")

# 全局性能监控实例
performance_monitor = PerformanceMonitor()

# 便捷装饰器
monitor_performance = performance_monitor.monitor_function

# 内存使用监控函数
def monitor_memory(interval=5):
    performance_monitor.monitor_memory_usage(interval)

# 内存使用上下文管理器
class MemoryUsageContext:
    def __enter__(self):
        self.start_time = time.time()
        self.start_memory = performance_monitor.get_memory_usage()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.end_memory = performance_monitor.get_memory_usage()
        self.execution_time = self.end_time - self.start_time
        
        memory_diff = {}
        if self.start_memory and self.end_memory:
            memory_diff['rss'] = self.end_memory['rss'] - self.start_memory['rss']
            memory_diff['vms'] = self.end_memory['vms'] - self.start_memory['vms']
        
        logger = logging.getLogger(__name__)
        logger.info(f"代码块执行时间: {self.execution_time:.4f} 秒")
        if memory_diff:
            logger.info(f"内存变化: RSS {memory_diff['rss']:.2f} MB, VMS {memory_diff['vms']:.2f} MB")

# 便捷上下文管理器
def measure_performance():
    return MemoryUsageContext()