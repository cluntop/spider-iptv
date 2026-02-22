import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.core.database import get_db
from src.utils.tools import Tools
from src.config.config import config

class ChannelService:
    def __init__(self):
        self.db = get_db()
        self.tools = Tools()
        self.logger = logging.getLogger(__name__)
    
    def get_categories(self):
        """获取所有启用的频道分类"""
        try:
            query = "SELECT psw, name, type FROM iptv_category WHERE enable = 1 ORDER BY id DESC"
            return self.db.fetchall(query)
        except Exception as e:
            self.logger.error(f"获取频道分类失败: {e}")
            return []
    
    def add_channel(self, name, url, channel_type=None, width=None, height=None, frame=None, speed=0.0, sign=0):
        """添加频道"""
        try:
            query = """
            INSERT INTO iptv_channels (name, url, type, width, height, frame, speed, sign, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                name = excluded.name,
                type = excluded.type,
                width = excluded.width,
                height = excluded.height,
                frame = excluded.frame,
                speed = excluded.speed,
                sign = excluded.sign,
                updated_at = excluded.updated_at
            """
            params = (name, url, channel_type, width, height, frame, speed, sign, datetime.now())
            self.db.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"添加频道失败: {name}, {url}, {e}")
            return False
    
    def batch_add_channels(self, channels):
        """批量添加频道"""
        if not channels:
            return 0
        
        try:
            query = """
            INSERT INTO iptv_channels (name, url, type, width, height, frame, speed, sign, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                name = excluded.name,
                type = excluded.type,
                width = excluded.width,
                height = excluded.height,
                frame = excluded.frame,
                speed = excluded.speed,
                sign = excluded.sign,
                updated_at = excluded.updated_at
            """
            params_list = [(ch[0], ch[1], ch[2], ch[3], ch[4], ch[5], ch[6], ch[7], datetime.now()) for ch in channels]
            cursor = self.db.executemany(query, params_list)
            return cursor.rowcount
        except Exception as e:
            self.logger.error(f"批量添加频道失败: {e}")
            return 0
    
    def update_channel_speed(self, channel_id, speed, width=None, height=None, frame=None):
        """更新频道速度和视频信息"""
        try:
            query = """
            UPDATE iptv_channels
            SET speed = ?, width = ?, height = ?, frame = ?, updated_at = ?
            WHERE id = ?
            """
            params = (speed, width, height, frame, datetime.now(), channel_id)
            self.db.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"更新频道速度失败: {channel_id}, {e}")
            return False
    
    def get_channels_to_check(self, limit=1000):
        """获取需要检查的频道"""
        try:
            query = """
            SELECT id, name, url, sign, speed
            FROM iptv_channels
            WHERE sign >= 0
            ORDER BY updated_at ASC
            LIMIT ?
            """
            return self.db.fetchall(query, (limit,))
        except Exception as e:
            self.logger.error(f"获取需要检查的频道失败: {e}")
            return []
    
    def check_channels_speed(self, channels, max_workers=5):
        """批量检查频道速度"""
        if not channels:
            return
        
        self.logger.info(f"开始检查 {len(channels)} 个频道的速度")
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            futures = {executor.submit(self._check_single_channel, channel): channel for channel in channels}
            
            # 处理结果
            for future in as_completed(futures):
                channel = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"检查频道速度异常: {channel[1]}, {e}")
        
        self.logger.info("频道速度检查完成")
    
    def _check_single_channel(self, channel):
        """检查单个频道的速度和视频信息"""
        channel_id, name, url, sign, speed = channel
        
        try:
            # 获取视频信息
            video_info = self.tools.get_ffprobe_info(url)
            if not video_info:
                self.logger.warning(f"无法获取视频信息: {name}, {url}")
                return
            
            width, height, frame = video_info
            
            # 如果速度为0，重新测试
            if speed == 0.0:
                speed = self.tools.get_ffmpeg_speed(url)
                if speed < config.validation.get('min_speed', 1.0):
                    self.logger.warning(f"频道速度过低: {name}, {speed} Mbps")
            
            # 更新频道信息
            self.update_channel_speed(channel_id, speed, width, height, frame)
            self.logger.info(f"更新频道信息: {name}, 速度: {speed} Mbps, 分辨率: {width}x{height}, 帧率: {frame}")
        except Exception as e:
            self.logger.error(f"检查频道失败: {name}, {url}, {e}")
    
    def get_valid_channels(self, category_type=None, limit=None):
        """获取有效的频道"""
        try:
            query = """
            SELECT name, url, type, speed
            FROM iptv_channels
            WHERE speed > ?
            """
            params = [config.validation.get('min_speed', 1.0)]
            
            if category_type:
                query += " AND type = ?"
                params.append(category_type)
            
            query += " ORDER BY speed DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            return self.db.fetchall(query, params)
        except Exception as e:
            self.logger.error(f"获取有效频道失败: {e}")
            return []
    
    def generate_iptv_playlist(self, output_file='source/iptv.txt'):
        """生成IPTV播放列表"""
        self.logger.info(f"开始生成IPTV播放列表: {output_file}")
        
        try:
            # 获取所有频道分类
            query_category = "SELECT type FROM iptv_category WHERE enable = 1 GROUP BY type ORDER BY id"
            categories = self.db.fetchall(query_category)
            
            result_pub = ""
            
            for category in categories:
                category_type = category[0]
                
                # 获取该分类下的频道
                query_channels = """
                SELECT c.name, c.url, c.id
                FROM iptv_channels c
                INNER JOIN iptv_category t ON c.name = t.name
                WHERE t.type = ? AND c.speed > ?
                ORDER BY c.speed DESC
                """
                channels = self.db.fetchall(query_channels, (category_type, config.validation.get('min_speed', 1.0)))
                
                # 添加分类标记
                result_pub += f"{category_type},#genre#\n"
                
                # 添加频道
                for channel in channels:
                    name, url, channel_id = channel
                    result_pub += f"{name},{url}\n"
                    
                    # 更新频道时间
                    self.db.execute("UPDATE iptv_channels SET updated_at = ? WHERE id = ?", (datetime.now(), channel_id))
            
            # 添加更新时间
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result_pub += f"更新时间,#genre#\n{update_time},https://taoiptv.com/time.mp4\n"
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result_pub)
            
            self.logger.info(f"成功生成IPTV播放列表: {output_file}")
            
            # 转换为m3u格式
            m3u_file = self.tools.convertToM3u(output_file)
            if m3u_file:
                self.logger.info(f"成功转换为m3u格式: {m3u_file}")
            
            return output_file
        except Exception as e:
            self.logger.error(f"生成IPTV播放列表失败: {e}")
            return None