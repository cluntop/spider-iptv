#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV系统测试脚本
"""
import sys
import os
import logging
import time
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.database import get_db
from src.services.source_service import SourceService
from src.services.channel_service import ChannelService
from src.services.hotel_service import HotelService
from src.services.multicast_service import MulticastService
from src.utils.tools import Tools
from src.utils.performance import measure_performance

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemTester:
    def __init__(self):
        self.tools = Tools()
        self.logger = logging.getLogger(__name__)
    
    def test_database_connection(self):
        """测试数据库连接"""
        self.logger.info("=== 测试数据库连接 ===")
        try:
            db = get_db()
            result = db.fetchone("SELECT 1")
            if result:
                self.logger.info("✅ 数据库连接正常")
                return True
            else:
                self.logger.error("❌ 数据库连接失败")
                return False
        except Exception as e:
            self.logger.error(f"❌ 数据库连接异常: {e}")
            return False
    
    def test_database_structure(self):
        """测试数据库结构"""
        self.logger.info("=== 测试数据库结构 ===")
        try:
            db = get_db()
            tables = ['iptv_category', 'iptv_channels', 'iptv_hotels', 'iptv_multicast', 'iptv_udpxy']
            for table in tables:
                result = db.fetchone(f"PRAGMA table_info({table})")
                if result:
                    self.logger.info(f"✅ 表 {table} 存在")
                else:
                    self.logger.warning(f"⚠️  表 {table} 不存在或无法访问")
            return True
        except Exception as e:
            self.logger.error(f"❌ 测试数据库结构异常: {e}")
            return False
    
    def test_tools(self):
        """测试工具类功能"""
        self.logger.info("=== 测试工具类功能 ===")
        try:
            # 测试IP地址校验
            test_ip = "192.168.1.1"
            if self.tools.check_ip(test_ip):
                self.logger.info(f"✅ IP地址校验正常: {test_ip}")
            else:
                self.logger.error(f"❌ IP地址校验失败: {test_ip}")
            
            # 测试URL有效性检查
            test_url = "https://www.baidu.com"
            if self.tools.check_url(test_url):
                self.logger.info(f"✅ URL检查正常: {test_url}")
            else:
                self.logger.warning(f"⚠️  URL检查失败: {test_url}")
            
            # 测试组播地址解析
            test_mcast = "rtp://239.1.1.1:1234"
            mcast_addr = self.tools.get_multicast_addr(test_mcast)
            if mcast_addr:
                self.logger.info(f"✅ 组播地址解析正常: {mcast_addr}")
            else:
                self.logger.error(f"❌ 组播地址解析失败: {test_mcast}")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ 测试工具类异常: {e}")
            return False
    
    def test_source_service(self):
        """测试数据源服务"""
        self.logger.info("=== 测试数据源服务 ===")
        try:
            source_service = SourceService()
            
            # 测试数据源下载
            with measure_performance():
                success, fail = source_service.download_sources()
                self.logger.info(f"✅ 数据源下载完成: 成功 {success}, 失败 {fail}")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ 测试数据源服务异常: {e}")
            return False
    
    def test_channel_service(self):
        """测试频道服务"""
        self.logger.info("=== 测试频道服务 ===")
        try:
            channel_service = ChannelService()
            
            # 测试获取频道分类
            categories = channel_service.get_categories()
            if categories:
                self.logger.info(f"✅ 频道分类获取成功: {len(categories)} 个")
            else:
                self.logger.warning("⚠️  未获取到频道分类")
            
            # 测试添加测试频道
            test_channel = ("测试频道", "https://example.com/stream", "测试", 1280, 720, 25, 5.0, 0)
            if channel_service.batch_add_channels([test_channel]):
                self.logger.info("✅ 测试频道添加成功")
            else:
                self.logger.warning("⚠️  测试频道添加失败")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ 测试频道服务异常: {e}")
            return False
    
    def test_hotel_service(self):
        """测试酒店服务"""
        self.logger.info("=== 测试酒店服务 ===")
        try:
            hotel_service = HotelService()
            
            # 测试添加测试酒店源
            test_hotel = ("192.168.1.1", "8080", "测试酒店", 10, 1)
            if hotel_service.add_hotel(*test_hotel):
                self.logger.info("✅ 测试酒店源添加成功")
            else:
                self.logger.warning("⚠️  测试酒店源添加失败")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ 测试酒店服务异常: {e}")
            return False
    
    def test_multicast_service(self):
        """测试组播服务"""
        self.logger.info("=== 测试组播服务 ===")
        try:
            multicast_service = MulticastService()
            
            # 测试添加测试组播
            test_multicast = ("中国", "北京", "电信", "source/multicast/北京-电信-239.1.1.txt", "北京", "http://127.0.0.1:4022", 1, 1)
            if multicast_service.add_multicast(*test_multicast):
                self.logger.info("✅ 测试组播添加成功")
            else:
                self.logger.warning("⚠️  测试组播添加失败")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ 测试组播服务异常: {e}")
            return False
    
    def test_performance(self):
        """测试系统性能"""
        self.logger.info("=== 测试系统性能 ===")
        try:
            from src.utils.performance import performance_monitor
            
            memory = performance_monitor.get_memory_usage()
            cpu = performance_monitor.get_cpu_usage()
            
            if memory:
                self.logger.info(f"✅ 内存使用: RSS {memory['rss']:.2f} MB, VMS {memory['vms']:.2f} MB")
            if cpu:
                self.logger.info(f"✅ CPU使用: {cpu['percent']:.1f}% ({cpu['cores']} 核心)")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ 测试系统性能异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self.logger.info(f"=== 开始系统测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        tests = [
            self.test_database_connection,
            self.test_database_structure,
            self.test_tools,
            self.test_source_service,
            self.test_channel_service,
            self.test_hotel_service,
            self.test_multicast_service,
            self.test_performance
        ]
        
        results = []
        for test in tests:
            result = test()
            results.append(result)
            time.sleep(1)  # 避免测试过于密集
        
        passed = sum(results)
        total = len(results)
        
        self.logger.info(f"=== 测试完成 - {passed}/{total} 通过 ===")
        if passed == total:
            self.logger.info("🎉 所有测试通过！系统状态正常")
        else:
            self.logger.warning(f"⚠️  部分测试失败，系统可能存在问题")
        
        return passed == total

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()