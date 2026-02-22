import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from src.core.database import get_db
from src.utils.tools import Tools
from src.config.config import config

class MulticastService:
    def __init__(self):
        self.db = get_db()
        self.tools = Tools()
        self.logger = logging.getLogger(__name__)
    
    def add_multicast(self, country, province, isp, path, city='', udpxy='', lines=0, status=0):
        """添加组播信息"""
        try:
            query = """
            INSERT INTO iptv_multicast (country, province, isp, path, city, udpxy, lines, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(province, isp) DO UPDATE SET
                country = excluded.country,
                path = excluded.path,
                city = excluded.city,
                udpxy = excluded.udpxy,
                lines = excluded.lines,
                status = excluded.status,
                updated_at = excluded.updated_at
            """
            params = (country, province, isp, path, city, udpxy, lines, status, datetime.now())
            self.db.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"添加组播信息失败: {province}-{isp}, {e}")
            return False
    
    def update_multicast(self, multicast_id, city=None, udpxy=None, lines=None, status=None):
        """更新组播信息"""
        try:
            updates = []
            params = []
            
            if city is not None:
                updates.append("city = ?")
                params.append(city)
            if udpxy is not None:
                updates.append("udpxy = ?")
                params.append(udpxy)
            if lines is not None:
                updates.append("lines = ?")
                params.append(lines)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now())
                params.append(multicast_id)
                
                query = f"UPDATE iptv_multicast SET {', '.join(updates)} WHERE id = ?"
                self.db.execute(query, params)
                return True
        except Exception as e:
            self.logger.error(f"更新组播信息失败: {multicast_id}, {e}")
        return False
    
    def get_multicasts(self):
        """获取所有组播信息"""
        try:
            query = """
            SELECT id, country, province, isp, path, city, udpxy, lines, status
            FROM iptv_multicast
            WHERE isp IS NOT NULL AND isp != ''
            ORDER BY id
            """
            return self.db.fetchall(query)
        except Exception as e:
            self.logger.error(f"获取组播信息失败: {e}")
            return []
    
    def add_udpxy(self, udpxy_id, mid, mcast, city, ip, port, actv=0, status=0):
        """添加udpxy代理"""
        try:
            query = """
            INSERT INTO iptv_udpxy (id, mid, mcast, city, ip, port, actv, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                mid = excluded.mid,
                mcast = excluded.mcast,
                city = excluded.city,
                ip = excluded.ip,
                port = excluded.port,
                actv = excluded.actv,
                status = excluded.status,
                updated_at = excluded.updated_at
            """
            params = (udpxy_id, mid, mcast, city, ip, port, actv, status, datetime.now())
            self.db.execute(query, params)
            return True
        except Exception as e:
            self.logger.error(f"添加udpxy代理失败: {ip}:{port}, {e}")
            return False
    
    def update_udpxy(self, udpxy_id, actv=None, status=None):
        """更新udpxy代理"""
        try:
            updates = []
            params = []
            
            if actv is not None:
                updates.append("actv = ?")
                params.append(actv)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now())
                params.append(udpxy_id)
                
                query = f"UPDATE iptv_udpxy SET {', '.join(updates)} WHERE id = ?"
                self.db.execute(query, params)
                return True
        except Exception as e:
            self.logger.error(f"更新udpxy代理失败: {udpxy_id}, {e}")
        return False
    
    def get_udpxy_by_mid(self, mid):
        """根据组播ID获取udpxy代理"""
        try:
            query = """
            SELECT id, city, ip, port, actv, status
            FROM iptv_udpxy
            WHERE mid = ? AND status = 1
            ORDER BY actv ASC, updated_at DESC
            """
            return self.db.fetchall(query, (mid,))
        except Exception as e:
            self.logger.error(f"获取udpxy代理失败: {mid}, {e}")
            return []
    
    def check_udpxy_status(self, ip, port):
        """检查udpxy代理状态"""
        try:
            status_url = f"http://{ip}:{port}/status"
            response = self.tools.request_body(status_url)
            
            if response:
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")
                client_table = soup.find('table', attrs={'cellspacing': '0'})
                
                if client_table:
                    td_tags = client_table.find_all('td')
                    if len(td_tags) >= 4:
                        actv = int(td_tags[3].text)
                        return 1, actv
            return 0, 0
        except Exception as e:
            self.logger.error(f"检查udpxy状态失败: {ip}:{port}, {e}")
            return 0, 0
    
    def fetch_udpxy_from_api(self, multicast, api_token):
        """从API获取udpxy代理"""
        try:
            mid = multicast[0]
            country = multicast[1]
            province = multicast[2]
            isp = multicast[3]
            mcast = f"{province}-{isp}"
            
            api_url = "https://quake.360.net/api/v3/search/quake_service"
            headers = {
                "X-QuakeToken": api_token,
                "Content-Type": "application/json"
            }
            
            data = {
                "query": f"udpxy AND country_cn: \"{country}\" AND province_cn: \"{province}\" AND isp: \"{isp}\"",
                "start": 0,
                "size": 10,
                "ignore_cache": False,
                "latest": True,
                "include": ["ip", "port", "location.city_cn"],
                "shortcuts": ["610ce2adb1a2e3e1632e67b2"]
            }
            
            response = requests.post(url=api_url, headers=headers, json=data, timeout=15)
            json_data = response.json()
            
            if json_data.get('code') == 0:
                udpxy_list = []
                for item in json_data.get('data', []):
                    udpxy_id = item.get('id')
                    ip = item.get('ip')
                    port = item.get('port')
                    city = item.get('location', {}).get('city_cn', '')
                    
                    # 检查udpxy状态
                    status, actv = self.check_udpxy_status(ip, port)
                    if status:
                        udpxy_list.append((udpxy_id, mid, mcast, city, ip, port, actv, status))
                        self.logger.info(f"发现有效udpxy代理: {ip}:{port}, 活跃度: {actv}")
                
                return udpxy_list
        except Exception as e:
            self.logger.error(f"从API获取udpxy代理失败: {mcast}, {e}")
        return []
    
    def process_multicast_channels(self, multicast, udpxy_list, channel_service):
        """处理组播频道"""
        try:
            mid, country, province, isp, path, city, udpxy_str, lines, status = multicast
            mcast = f"{province}-{isp}"
            
            # 读取组播文件
            if path.endswith('.m3u'):
                txt_path = self.tools.convertToTxt(path)
                if not txt_path:
                    self.logger.warning(f"组播文件转换失败: {path}")
                    return
                path = txt_path
            
            # 读取文件内容
            with open(path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # 获取频道分类
            categories = channel_service.get_categories()
            
            # 处理每个udpxy代理
            valid_udpxy = []
            valid_cities = []
            
            for udpxy_info in udpxy_list:
                udpxy_id, udpxy_city, ip, port, actv, udpxy_status = udpxy_info
                
                if udpxy_status != 1:
                    continue
                
                udpxy_url = f"http://{ip}:{port}"
                
                # 处理频道
                valid_channels = []
                error_cnt = 0
                sum_speed = 0.0
                
                for line in lines:
                    line = line.strip()
                    if ',' not in line or 'CAVS' in line or '测试' in line:
                        continue
                    
                    # 提取频道信息
                    parts = line.split(',', 1)
                    if len(parts) != 2:
                        continue
                    
                    ch_name, ch_url = parts
                    ch_name = ch_name.replace('#EXTINF-1', '').strip()
                    
                    # 处理组播地址
                    m3u8_link = self.tools.get_multicast_addr(ch_url)
                    if not m3u8_link:
                        continue
                    
                    # 构建完整URL
                    full_url = f"{udpxy_url}/rtp/{m3u8_link}"
                    
                    # 匹配频道分类
                    category = self.tools.get_category(ch_name, categories)
                    category_type = category[1]
                    
                    if category_type:
                        # 测试速度
                        speed = self.tools.get_ffmpeg_speed(full_url)
                        if speed < config.validation.get('min_speed', 5.0):
                            error_cnt += 1
                            if error_cnt >= 3:
                                break
                        else:
                            sum_speed += speed
                            
                            # 获取视频信息
                            video_info = self.tools.get_ffprobe_info(full_url)
                            width, height, frame = video_info if video_info else (1280, 720, 25)
                            
                            valid_channels.append((category[0], full_url, category_type, width, height, frame, speed, 2))
                
                if error_cnt < 3 and valid_channels:
                    # 添加频道
                    channel_service.batch_add_channels(valid_channels)
                    valid_udpxy.append(udpxy_url)
                    valid_cities.append(udpxy_city)
                    self.logger.info(f"组播代理处理完成: {udpxy_url}, 有效频道: {len(valid_channels)}")
            
            # 更新组播信息
            if valid_udpxy:
                self.update_multicast(mid, city=','.join(valid_cities), udpxy=','.join(valid_udpxy), 
                                     lines=len(valid_udpxy), status=1)
            else:
                self.update_multicast(mid, status=0)
                self.logger.warning(f"无有效udpxy代理: {mcast}")
        except Exception as e:
            self.logger.error(f"处理组播频道失败: {multicast[2]}-{multicast[3]}, {e}")