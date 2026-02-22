import os
import re
import time
import json
import subprocess
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Tools:
    def __init__(self):
        # 创建会话对象，使用连接池
        self.session = requests.Session()
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        # 设置默认超时
        self.session.timeout = 30
    
    def check_ip(self, ip):
        """校验是否为ip地址"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return bool(re.match(pattern, ip))
    
    def get_multicast_addr(self, url):
        """获取组播地址"""
        match = re.search(r'(rtp/|rtp://|udp/|udp://)(.*)', url)
        if match:
            return match.group(2)
        return None
    
    def check_url(self, url, timeout=3):
        """检查URL的有效性"""
        return self.valid_url(url, timeout)
    
    def valid_url(self, url, timeout):
        """验证URL的有效性"""
        try:
            response = self.session.get(url, stream=True, timeout=timeout)
            return response.status_code == 200
        except RequestException:
            return False
    
    def check_iptv(self, url, delay=5):
        """检查IPTV的有效性"""
        try:
            response = self.session.get(url, timeout=delay)
            if response.status_code == 200:
                response_time = response.elapsed.total_seconds()
                return response_time <= delay
            return False
        except requests.RequestException:
            return False
    
    def request_body(self, url, timeout=10):
        """发起HTTP请求获取网页内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
            }
            response = self.session.get(url, timeout=timeout, headers=headers)
            if response.status_code == 200:
                return response
            return None
        except (requests.Timeout, requests.RequestException):
            return None
    
    def get_ip_guishu(self, ip):
        """获取IP归属地"""
        ip_url = f'https://www.ipshudi.com/{ip}.htm'
        str_guishu = ''
        
        try:
            response = self.request_body(ip_url)
            if response:
                response.encoding = 'utf-8'
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                table = soup.find('table')
                if table:
                    raw_list = table.find_all('tr')
                    if len(raw_list) > 2:
                        ip_add = raw_list[1].find_all('td')[1].text.replace('上报纠错', '').replace(' ', '').strip()
                        ip_ips = raw_list[2].find_all('td')[1].text.replace('上报纠错', '').replace(' ', '').strip()
                        str_guishu = f"{ip_add}【{ip_ips}】"
            return str_guishu
        except Exception:
            return str_guishu
    
    def get_ffprobe_info(self, url):
        """解析IPTV分辨率等信息"""
        command = ['ffprobe', '-print_format', 'json', '-show_format', '-show_streams', '-v', 'quiet', url]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            output = result.stdout
            data = json.loads(output)
            
            if 'streams' in data:
                video_streams = data['streams']
                if video_streams:
                    stream = video_streams[0]
                    width = stream.get('width', 0)
                    height = stream.get('height', 0)
                    frame = stream.get('r_frame_rate', '0/0')
                    
                    if frame and frame != '0/0':
                        num, den = map(int, frame.split('/'))
                        frame_rate = num / den if den != 0 else 0
                    else:
                        frame_rate = 0
                    
                    if width > 0 and height > 0 and frame_rate > 0:
                        return [width, height, frame_rate]
            return []
        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, ValueError):
            return []
    
    def get_speed(self, url, fornum=3):
        """获取IPTV播放速度信息"""
        try:
            speeds = []
            for _ in range(fornum):
                start_time = time.time()
                response = self.session.get(url, stream=True, timeout=10)
                total_bytes = 0
                
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        total_bytes += len(chunk)
                
                response.close()
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    speed = total_bytes / elapsed_time / 1024  # Kbps
                    speeds.append(speed)
                time.sleep(2)
            
            if speeds:
                average_speed = sum(speeds) / len(speeds)
                return round(average_speed, 2)
            return 0.00
        except (requests.Timeout, requests.RequestException):
            return 0.00
    
    def get_ffmpeg_speed(self, url, delay=10):
        """获取IPTV播放速度信息（使用ffmpeg）"""
        try:
            ffmpeg_command = f"ffmpeg -i {url} -t {delay} -f null -"
            process = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=20)
            
            output_str = stderr.decode("utf-8", errors="ignore")
            match = re.findall(r'speed=(.*?)x', output_str)
            
            if match:
                speeds = [float(speed) for speed in match if speed.replace('.', '').isdigit()]
                if speeds:
                    avg_speed = sum(speeds) / len(speeds)
                    speed_mbps = round(avg_speed, 2)
                    return speed_mbps if speed_mbps >= 1.0 else 0.00
            return 0.00
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, re.error):
            return 0.00
    
    def get_category(self, str_name, category_list):
        """获取频道分类"""
        category_type = None
        category_name = None
        
        for category_info in category_list:
            if category_type:
                break
            
            category_psw = category_info[0]
            category_name = category_info[1]
            name_values = category_psw.split(',')
            
            type_alist = ('CCTV1', 'CCTV4', 'CCTV5', 'CCTV8', 'CGTN')
            type_blist = ('CCTV10', 'CCTV11', 'CCTV12', 'CCTV13', 'CCTV14', 'CCTV15', 'CCTV16', 'CCTV17', 'CCTV4K', 'CCTV4欧洲', 'CCTV4美洲', 'CCTV5+', 'CCTV8K', 'CGTN法语', 'CGTN俄语', 'CGTN阿语', 'CGTN西语', 'CGTN记录')
            
            if category_name in type_alist:
                if any(name_value in str_name for name_value in name_values) and not any(type_b in str_name for type_b in type_blist):
                    category_type = category_info[2]
                    break
            else:
                if any(name_value in str_name for name_value in name_values):
                    category_type = category_info[2]
                    break
        
        return (category_name, category_type)
    
    def convertToM3u(self, txt_file):
        """将txt文件转换为m3u格式"""
        if not txt_file.endswith('.txt'):
            return None
        
        m3u_file = txt_file[:-4] + '.m3u'
        current_group = None
        
        try:
            with open(txt_file, 'r', encoding='utf-8') as file, \
                 open(m3u_file, 'w', encoding='utf-8') as out_file:
                # 写入m3u头部
                out_file.write('#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"\n')
                
                for line in file:
                    trimmed_line = line.strip()
                    if not trimmed_line:
                        continue
                    
                    if '#genre#' in trimmed_line:
                        current_group = trimmed_line.replace(',#genre#', '').strip()
                    elif ',' in trimmed_line:
                        parts = trimmed_line.split(',', 1)
                        if len(parts) != 2:
                            continue
                        original_channel_name, channel_link = [item.strip() for item in parts]
                        
                        # 构建EXTINF行
                        extinf_line = f'#EXTINF:-1 tvg-name="{original_channel_name}" tvg-logo="https://live.fanmingming.com/tv/{original_channel_name}.png"'
                        if current_group:
                            extinf_line += f' group-title="{current_group}"'
                        extinf_line += f',{original_channel_name}\n'
                        
                        # 写入文件
                        out_file.write(extinf_line)
                        out_file.write(f'{channel_link}\n')
            
            return m3u_file
        except Exception as e:
            import logging
            logging.error(f"转换文件失败: {txt_file}, {e}")
            return None
    
    def convertToTxt(self, m3u_file):
        """将m3u文件转换为txt格式"""
        if not m3u_file.endswith('.m3u'):
            return None
        
        txt_file = m3u_file[:-4] + '.txt'
        
        try:
            with open(m3u_file, 'r', encoding='utf-8') as file, \
                 open(txt_file, 'w', encoding='utf-8') as out_file:
                lines = iter(file)
                for line in lines:
                    trimmed_line = line.strip()
                    if trimmed_line.startswith('#EXTINF'):
                        try:
                            next_line = next(lines).strip()
                            if next_line:
                                channel_name = trimmed_line[trimmed_line.rfind(',') + 1:].strip()
                                out_file.write(f"{channel_name},{next_line}\n")
                        except StopIteration:
                            break
            
            return txt_file
        except Exception as e:
            import logging
            logging.error(f"转换文件失败: {m3u_file}, {e}")
            return None