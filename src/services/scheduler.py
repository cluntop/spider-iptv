import logging
import time
from datetime import datetime, timedelta
from threading import Thread
from src.config.config import config
from src.services.source_service import SourceService
from src.services.channel_service import ChannelService
from src.services.hotel_service import HotelService
from src.services.multicast_service import MulticastService

class Scheduler:
    def __init__(self):
        self.source_service = SourceService()
        self.channel_service = ChannelService()
        self.hotel_service = HotelService()
        self.multicast_service = MulticastService()
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.last_download_time = None
        self.last_check_time = None
        self.last_cleanup_time = None
    
    def start(self):
        """启动调度器"""
        self.running = True
        self.logger.info("调度器启动")
        
        # 启动主调度线程
        schedule_thread = Thread(target=self._schedule_loop)
        schedule_thread.daemon = True
        schedule_thread.start()
    
    def stop(self):
        """停止调度器"""
        self.running = False
        self.logger.info("调度器停止")
    
    def _schedule_loop(self):
        """调度循环"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # 检查是否需要下载数据源
                if self._should_download(current_time):
                    self._download_sources()
                    self.last_download_time = current_time
                
                # 检查是否需要检查频道
                if self._should_check(current_time):
                    self._check_channels()
                    self.last_check_time = current_time
                
                # 检查是否需要清理
                if self._should_cleanup(current_time):
                    self._cleanup_data()
                    self.last_cleanup_time = current_time
                
                # 休眠一段时间
                time.sleep(60)  # 每分钟检查一次
            except Exception as e:
                self.logger.error(f"调度循环失败: {e}")
                time.sleep(60)
    
    def _should_download(self, current_time):
        """判断是否需要下载数据源"""
        interval = config.scheduler.get('download_interval', 24)  # 小时
        if not self.last_download_time:
            return True
        return (current_time - self.last_download_time).total_seconds() >= interval * 3600
    
    def _should_check(self, current_time):
        """判断是否需要检查频道"""
        interval = config.scheduler.get('check_interval', 6)  # 小时
        if not self.last_check_time:
            return True
        return (current_time - self.last_check_time).total_seconds() >= interval * 3600
    
    def _should_cleanup(self, current_time):
        """判断是否需要清理数据"""
        interval = config.scheduler.get('cleanup_interval', 72)  # 小时
        if not self.last_cleanup_time:
            return True
        return (current_time - self.last_cleanup_time).total_seconds() >= interval * 3600
    
    def _download_sources(self):
        """下载数据源"""
        self.logger.info("开始自动下载数据源")
        
        # 下载网络数据源
        success, fail = self.source_service.download_sources()
        self.logger.info(f"网络数据源下载完成: 成功 {success}, 失败 {fail}")
        
        # 抓取四川组播数据
        if self.source_service.fetch_sichuan_multicast():
            self.logger.info("四川组播数据抓取成功")
        else:
            self.logger.warning("四川组播数据抓取失败")
        
        # 从gyssi.link抓取酒店源
        hotels = self.source_service.fetch_gyssi_hotels()
        if hotels:
            count = self.hotel_service.batch_add_hotels(hotels)
            self.logger.info(f"添加酒店源完成: {count} 个")
        else:
            self.logger.warning("未发现有效酒店源")
        
        # 抓取网络直播源
        txt_file = self.source_service.fetch_internet_lives()
        if txt_file:
            self.logger.info("网络直播源抓取成功")
        else:
            self.logger.warning("网络直播源抓取失败")
    
    def _check_channels(self):
        """检查频道"""
        self.logger.info("开始自动检查频道")
        
        # 检查频道速度
        channels = self.channel_service.get_channels_to_check(limit=1000)
        if channels:
            self.channel_service.check_channels_speed(channels, max_workers=5)
        else:
            self.logger.warning("没有需要检查的频道")
        
        # 处理酒店源频道
        hotels_to_check = self.hotel_service.get_hotels_to_check()
        for hotel in hotels_to_check:
            ip, port, status = hotel
            # 扫描酒店网络段
            if last_dot := ip.rfind('.'):
                base_ip = ip[:last_dot]
                valid_hotels = self.hotel_service.scan_hotel_network(base_ip, port)
                if valid_hotels:
                    self.hotel_service.batch_add_hotels(valid_hotels)
        
        # 处理酒店源频道
        from src.core.database import get_db
        db = get_db()
        hotels_to_process = db.fetchall("SELECT ip, port, name, count, status, updated_at FROM iptv_hotels WHERE status = 1")
        for hotel in hotels_to_process:
            self.hotel_service.process_hotel_channels(hotel, self.channel_service)
        
        # 生成IPTV播放列表
        playlist_file = self.channel_service.generate_iptv_playlist()
        if playlist_file:
            self.logger.info(f"IPTV播放列表生成成功: {playlist_file}")
        else:
            self.logger.warning("IPTV播放列表生成失败")
    
    def _cleanup_data(self):
        """清理数据"""
        self.logger.info("开始自动清理数据")
        
        from src.core.database import get_db
        db = get_db()
        
        try:
            # 删除无效频道（速度为0且超过7天未更新）
            cutoff_time = datetime.now() - timedelta(days=7)
            query = "DELETE FROM iptv_channels WHERE speed = 0 AND updated_at < ?"
            db.execute(query, (cutoff_time,))
            self.logger.info("清理无效频道完成")
            
            # 删除无效酒店源（状态为0且超过7天未更新）
            query = "DELETE FROM iptv_hotels WHERE status = 0 AND updated_at < ?"
            db.execute(query, (cutoff_time,))
            self.logger.info("清理无效酒店源完成")
            
            # 删除无效udpxy代理（状态为0且超过7天未更新）
            query = "DELETE FROM iptv_udpxy WHERE status = 0 AND updated_at < ?"
            db.execute(query, (cutoff_time,))
            self.logger.info("清理无效udpxy代理完成")
        except Exception as e:
            self.logger.error(f"清理数据失败: {e}")
    
    def run_once(self):
        """运行一次所有任务"""
        self.logger.info("手动运行所有任务")
        
        # 下载数据源
        self._download_sources()
        
        # 检查频道
        self._check_channels()
        
        # 清理数据
        self._cleanup_data()
        
        self.logger.info("手动运行任务完成")