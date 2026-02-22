#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV爬虫主程序
"""
import logging
import time
from datetime import datetime
from src.config.config import config
from src.services.source_service import SourceService
from src.services.channel_service import ChannelService
from src.services.hotel_service import HotelService
from src.services.multicast_service import MulticastService
from src.core.database import get_db

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.logging.get('level', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IPTVSpider:
    def __init__(self):
        self.source_service = SourceService()
        self.channel_service = ChannelService()
        self.hotel_service = HotelService()
        self.multicast_service = MulticastService()
        self.db = get_db()
        logger.info("IPTV爬虫初始化完成")
    
    def run(self):
        """运行主程序"""
        try:
            logger.info("开始运行IPTV爬虫")
            
            # 1. 下载数据源
            self._download_sources()
            
            # 2. 处理酒店源
            self._process_hotels()
            
            # 3. 处理组播
            self._process_multicast()
            
            # 4. 处理网络直播源
            self._process_internet_lives()
            
            # 5. 检查频道速度
            self._check_channels_speed()
            
            # 6. 生成IPTV播放列表
            self._generate_playlist()
            
            logger.info("IPTV爬虫运行完成")
        except Exception as e:
            logger.error(f"主程序运行失败: {e}")
    
    def _download_sources(self):
        """下载数据源"""
        logger.info("开始下载数据源")
        
        # 下载网络数据源
        success, fail = self.source_service.download_sources()
        logger.info(f"网络数据源下载完成: 成功 {success}, 失败 {fail}")
        
        # 抓取四川组播数据
        if self.source_service.fetch_sichuan_multicast():
            logger.info("四川组播数据抓取成功")
        else:
            logger.warning("四川组播数据抓取失败")
    
    def _process_hotels(self):
        """处理酒店源"""
        logger.info("开始处理酒店源")
        
        # 从gyssi.link抓取酒店源
        hotels = self.source_service.fetch_gyssi_hotels()
        if hotels:
            count = self.hotel_service.batch_add_hotels(hotels)
            logger.info(f"添加酒店源完成: {count} 个")
        else:
            logger.warning("未发现有效酒店源")
        
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
        hotels_to_process = self.db.fetchall("SELECT ip, port, name, count, status, updated_at FROM iptv_hotels WHERE status = 1")
        for hotel in hotels_to_process:
            self.hotel_service.process_hotel_channels(hotel, self.channel_service)
    
    def _process_multicast(self):
        """处理组播"""
        logger.info("开始处理组播")
        
        # 获取组播信息
        multicasts = self.multicast_service.get_multicasts()
        
        # 处理每个组播
        for multicast in multicasts:
            mid, country, province, isp, path, city, udpxy, lines, status = multicast
            
            # 获取udpxy代理
            udpxy_list = self.multicast_service.get_udpxy_by_mid(mid)
            
            # 如果没有udpxy代理，尝试从API获取
            if not udpxy_list:
                # 注意：这里需要设置有效的API token
                api_token = config.get('api.token', '')
                if api_token:
                    new_udpxy = self.multicast_service.fetch_udpxy_from_api(multicast, api_token)
                    for udpxy_info in new_udpxy:
                        self.multicast_service.add_udpxy(*udpxy_info)
                    udpxy_list = self.multicast_service.get_udpxy_by_mid(mid)
            
            # 处理组播频道
            if udpxy_list:
                self.multicast_service.process_multicast_channels(multicast, udpxy_list, self.channel_service)
    
    def _process_internet_lives(self):
        """处理网络直播源"""
        logger.info("开始处理网络直播源")
        
        # 抓取网络直播源
        txt_file = self.source_service.fetch_internet_lives()
        if txt_file:
            # 读取文件内容
            try:
                with open(txt_file, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                # 处理频道
                valid_channels = []
                categories = self.channel_service.get_categories()
                
                for line in lines:
                    line = line.strip()
                    if ',' not in line or 'http' not in line:
                        continue
                    
                    parts = line.split(',', 1)
                    if len(parts) != 2:
                        continue
                    
                    ch_name, ch_url = parts
                    ch_name = ch_name.replace('#EXTINF-1', '').strip()
                    
                    # 匹配频道分类
                    category = self.channel_service.tools.get_category(ch_name, categories)
                    category_type = category[1]
                    
                    if category_type:
                        # 获取视频信息
                        video_info = self.channel_service.tools.get_ffprobe_info(ch_url)
                        width, height, frame = video_info if video_info else (1280, 720, 25)
                        
                        valid_channels.append((category[0], ch_url, category_type, width, height, frame, 5.0, 0))
                
                if valid_channels:
                    count = self.channel_service.batch_add_channels(valid_channels)
                    logger.info(f"添加网络直播源完成: {count} 个")
                else:
                    logger.warning("未发现有效网络直播源")
            except Exception as e:
                logger.error(f"处理网络直播源失败: {e}")
    
    def _check_channels_speed(self):
        """检查频道速度"""
        logger.info("开始检查频道速度")
        
        # 获取需要检查的频道
        channels = self.channel_service.get_channels_to_check(limit=1000)
        if channels:
            self.channel_service.check_channels_speed(channels, max_workers=5)
        else:
            logger.warning("没有需要检查的频道")
    
    def _generate_playlist(self):
        """生成IPTV播放列表"""
        logger.info("开始生成IPTV播放列表")
        
        # 生成播放列表
        playlist_file = self.channel_service.generate_iptv_playlist()
        if playlist_file:
            logger.info(f"IPTV播放列表生成成功: {playlist_file}")
        else:
            logger.warning("IPTV播放列表生成失败")

import sys

if __name__ == "__main__":
    try:
        # 检查是否为初始爬取模式
        initial_crawl = "--initial-crawl" in sys.argv
        
        # 初始化数据库
        print("正在初始化数据库...")
        db = get_db()
        print("数据库初始化完成")
        
        # 运行爬虫
        print("正在运行IPTV爬虫...")
        spider = IPTVSpider()
        spider.run()
        print("IPTV爬虫运行完成")
        
        if not initial_crawl:
            # 启动数据库健康检查
            from src.services.db_health import DatabaseHealthChecker
            health_checker = DatabaseHealthChecker()
            health_checker.start()
            print("数据库健康检查已启动")
            
            # 启动调度器
            from src.services.scheduler import Scheduler
            scheduler = Scheduler()
            scheduler.start()
            print("自动调度器已启动")
            
            # 保持程序运行
            print("程序已启动，按 Ctrl+C 退出...")
            while True:
                time.sleep(1)
        else:
            print("初始爬取完成，程序退出")
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        try:
            scheduler.stop()
            health_checker.stop()
        except:
            pass
    except Exception as e:
        print(f"\n程序启动失败: {e}")
        import traceback
        traceback.print_exc()