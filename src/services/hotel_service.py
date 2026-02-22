import logging
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.core.database import get_db
from src.utils.tools import Tools
from src.config.config import config

class HotelService:
    def __init__(self):
        self.db = get_db()
        self.tools = Tools()
        self.logger = logging.getLogger(__name__)
    
    def add_hotel(self, ip, port, name='', count=0, status=0):
        """添加酒店源"""
        try:
            query = """
            INSERT INTO iptv_hotels (ip, port, name, count, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(ip, port) DO UPDATE SET
                name = excluded.name,
                count = excluded.count,
                status = excluded.status,
                updated_at = excluded.updated_at
            """
            params = (ip, port, name, count, status, datetime.now())
            self.db.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"添加酒店源失败: {ip}:{port}, {e}")
            return False
    
    def batch_add_hotels(self, hotels):
        """批量添加酒店源"""
        if not hotels:
            return 0
        
        try:
            query = """
            INSERT INTO iptv_hotels (ip, port, name, count, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(ip, port) DO UPDATE SET
                name = excluded.name,
                count = excluded.count,
                status = excluded.status,
                updated_at = excluded.updated_at
            """
            params_list = [(h[0], h[1], h[2], h[3], h[4], datetime.now()) for h in hotels]
            cursor = self.db.executemany(query, params_list)
            return cursor.rowcount
        except Exception as e:
            self.logger.error(f"批量添加酒店源失败: {e}")
            return 0
    
    def update_hotel(self, ip, port, name=None, count=None, status=None):
        """更新酒店源"""
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if count is not None:
                updates.append("count = ?")
                params.append(count)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now())
                params.extend([ip, port])
                
                query = f"UPDATE iptv_hotels SET {', '.join(updates)} WHERE ip = ? AND port = ?"
                self.db.execute(query, params)
                return True
        except Exception as e:
            self.logger.error(f"更新酒店源失败: {ip}:{port}, {e}")
        return False
    
    def get_hotels_to_check(self):
        """获取需要检查的酒店源"""
        try:
            query = """
            SELECT ip, port, status
            FROM iptv_hotels
            WHERE status IN (0, 1)
            ORDER BY updated_at ASC
            """
            return self.db.fetchall(query)
        except Exception as e:
            self.logger.error(f"获取需要检查的酒店源失败: {e}")
            return []
    
    def scan_hotel_network(self, base_ip, port, max_workers=10):
        """扫描酒店网络段"""
        self.logger.info(f"开始扫描酒店网络段: {base_ip}.*:{port}")
        
        # 生成IP列表
        ips = [f"{base_ip}.{i}" for i in range(1, 256)]
        ip_port_list = [(ip, port) for ip in ips]
        
        valid_hotels = []
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            futures = {executor.submit(self._check_hotel_connectivity, ip, port): (ip, port) for ip, port in ip_port_list}
            
            # 处理结果
            for future in as_completed(futures):
                ip, port = futures[future]
                try:
                    is_valid, speed = future.result()
                    if is_valid:
                        valid_hotels.append((ip, port, '扫描检查更新酒店源', 1, 1, datetime.now()))
                        self.logger.info(f"发现有效酒店源: {ip}:{port}, 速度: {speed} Mbps")
                except Exception as e:
                    self.logger.error(f"扫描酒店源异常: {ip}:{port}, {e}")
        
        self.logger.info(f"扫描完成，发现 {len(valid_hotels)} 个有效酒店源")
        return valid_hotels
    
    def _check_hotel_connectivity(self, ip, port):
        """检查酒店源连接性"""
        try:
            # 检查端口是否开放
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, int(port)))
            sock.close()
            
            if result == 0:
                # 检查播放速度
                test_url = f"http://{ip}:{port}/tsfile/live/0003_1.m3u8?key=txiptv"
                speed1 = self.tools.get_ffmpeg_speed(test_url)
                
                test_url2 = f"http://{ip}:{port}/tsfile/live/0006_1.m3u8?key=txiptv"
                speed2 = self.tools.get_ffmpeg_speed(test_url2)
                
                total_speed = speed1 + speed2
                if total_speed > 2.0:
                    return True, total_speed
            return False, 0.0
        except Exception:
            return False, 0.0
    
    def check_hotel_channels(self, ip, port):
        """检查酒店源频道"""
        try:
            url = f"http://{ip}:{port}/iptv/live/1000.json?key=txiptv"
            import requests
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                json_data = response.json()
                if 'data' in json_data:
                    channels = []
                    for item in json_data['data']:
                        name = item.get('name', '')
                        m3u8_link = item.get('url', '')
                        if '.m3u8' in m3u8_link and 'http' not in m3u8_link:
                            full_url = f"http://{ip}:{port}{m3u8_link}"
                            channels.append((name, full_url))
                    return channels
        except Exception as e:
            self.logger.error(f"检查酒店源频道失败: {ip}:{port}, {e}")
        return []
    
    def process_hotel_channels(self, hotel, channel_service):
        """处理酒店源频道"""
        ip, port, name, count, status, updated_at = hotel
        
        try:
            # 检查酒店源频道
            channels = self.check_hotel_channels(ip, port)
            if not channels:
                self.logger.warning(f"酒店源无有效频道: {ip}:{port}")
                self.update_hotel(ip, port, status=0, count=0)
                return
            
            # 获取频道分类
            categories = channel_service.get_categories()
            
            # 处理频道
            valid_channels = []
            error_cnt = 0
            sum_speed = 0.0
            
            for i, (ch_name, ch_url) in enumerate(channels):
                if i >= 3 and error_cnt >= 3:
                    break
                
                # 匹配频道分类
                category = self.tools.get_category(ch_name, categories)
                category_type = category[1]
                
                if category_type:
                    # 测试速度
                    speed = self.tools.get_ffmpeg_speed(ch_url)
                    if speed < config.validation.get('min_speed', 2.0):
                        error_cnt += 1
                        self.logger.warning(f"频道速度过低: {ch_name}, {speed} Mbps")
                    else:
                        sum_speed += speed
                        
                        # 获取视频信息
                        video_info = self.tools.get_ffprobe_info(ch_url)
                        width, height, frame = video_info if video_info else (1280, 720, 25)
                        
                        valid_channels.append((category[0], ch_url, category_type, width, height, frame, speed, 1))
            
            if error_cnt < 3:
                # 计算平均速度
                avg_speed = sum_speed / (3 - error_cnt) if (3 - error_cnt) > 0 else 0
                
                # 批量添加频道
                channel_service.batch_add_channels(valid_channels)
                
                # 更新酒店源状态
                source_name = self.tools.get_ip_guishu(ip)
                self.update_hotel(ip, port, name=source_name, count=len(valid_channels), status=1)
                
                self.logger.info(f"处理酒店源完成: {ip}:{port}, 有效频道: {len(valid_channels)}, 状态: 1")
            else:
                # 标记为无效
                self.update_hotel(ip, port, status=0, count=0)
                self.logger.warning(f"酒店源无效: {ip}:{port}, 错误计数: {error_cnt}")
        except Exception as e:
            self.logger.error(f"处理酒店源频道失败: {ip}:{port}, {e}")
            self.update_hotel(ip, port, status=0, count=0)