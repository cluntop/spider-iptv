import os
import re
import time
import json
import subprocess
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        # 设置默认超时
        self.session.timeout = 30
        self.logger = logging.getLogger(__name__)
        self.ffmpeg_available = self._check_ffmpeg_availability()
    
    def _check_ffmpeg_availability(self):
        """检查ffmpeg是否可用"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            self.logger.warning("ffmpeg not found, some features will be disabled")
            return False
    
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
            response = self.session.get(url, stream=True, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            return response.status_code == 200
        except RequestException:
            return False
    
    def check_iptv(self, url, delay=5):
        """检查IPTV的有效性"""
        try:
            response = self.session.get(url, timeout=delay, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
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
            response = self.session.get(url, timeout=timeout, headers=headers, stream=True)
            if response.status_code == 200:
                return response
            return None
        except (requests.Timeout, requests.RequestException) as e:
            self.logger.debug(f"Request failed: {url}, {e}")
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
        except Exception as e:
            self.logger.debug(f"Get IP location failed: {ip}, {e}")
            return str_guishu
    
    def get_ffprobe_info(self, url):
        """解析IPTV分辨率等信息"""
        if not self.ffmpeg_available:
            return []
        
        command = ['ffprobe', '-print_format', 'json', '-show_format', '-show_streams', '-v', 'quiet', url]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            output = result.stdout
            data = json.loads(output)
            
            if 'streams' in data:
                video_streams = [stream for stream in data['streams'] if stream.get('codec_type') == 'video']
                if video_streams:
                    stream = video_streams[0]
                    width = stream.get('width', 0)
                    height = stream.get('height', 0)
                    frame = stream.get('r_frame_rate', '0/0')
                    
                    if frame and frame != '0/0':
                        try:
                            num, den = map(int, frame.split('/'))
                            frame_rate = num / den if den != 0 else 0
                        except (ValueError, ZeroDivisionError):
                            frame_rate = 0
                    else:
                        frame_rate = 0
                    
                    if width > 0 and height > 0 and frame_rate > 0:
                        return [width, height, frame_rate]
            return []
        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.debug(f"FFprobe failed: {url}, {e}")
            return []
    
    def get_speed(self, url, fornum=3):
        """获取IPTV播放速度信息"""
        try:
            speeds = []
            for _ in range(fornum):
                start_time = time.time()
                response = self.session.get(url, stream=True, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                total_bytes = 0
                
                # 读取最多1MB数据
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        total_bytes += len(chunk)
                        if total_bytes >= 1024 * 1024:
                            break
                
                response.close()
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    speed = total_bytes / elapsed_time / 1024  # Kbps
                    speeds.append(speed)
                time.sleep(1)  # 减少间隔，提高效率
            
            if speeds:
                average_speed = sum(speeds) / len(speeds)
                return round(average_speed, 2)
            return 0.00
        except (requests.Timeout, requests.RequestException) as e:
            self.logger.debug(f"Get speed failed: {url}, {e}")
            return 0.00
    
    def get_ffmpeg_speed(self, url, delay=10):
        """获取IPTV播放速度信息（使用ffmpeg）"""
        if not self.ffmpeg_available:
            return 0.00
        
        try:
            ffmpeg_command = f"ffmpeg -i {url} -t {delay} -f null -"
            process = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=delay + 5)
            
            output_str = stderr.decode("utf-8", errors="ignore")
            match = re.findall(r'speed=(.*?)x', output_str)
            
            if match:
                speeds = []
                for speed in match:
                    try:
                        if speed.replace('.', '').isdigit():
                            speeds.append(float(speed))
                    except ValueError:
                        pass
                if speeds:
                    avg_speed = sum(speeds) / len(speeds)
                    speed_mbps = round(avg_speed, 2)
                    return speed_mbps if speed_mbps >= 1.0 else 0.00
            return 0.00
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, re.error) as e:
            self.logger.debug(f"FFmpeg speed test failed: {url}, {e}")
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
            # 确保目录存在
            os.makedirs(os.path.dirname(m3u_file), exist_ok=True)
            
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as file, \
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
            self.logger.error(f"Convert file failed: {txt_file}, {e}")
            return None
    
    def convertToTxt(self, m3u_file):
        """将m3u文件转换为txt格式"""
        if not m3u_file.endswith('.m3u'):
            return None
        
        txt_file = m3u_file[:-4] + '.txt'
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(txt_file), exist_ok=True)
            
            with open(m3u_file, 'r', encoding='utf-8', errors='ignore') as file, \
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
            self.logger.error(f"Convert file failed: {m3u_file}, {e}")
            return None
    
    def batch_check_urls(self, urls, timeout=3, max_workers=10):
        """批量检查URL的有效性"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.valid_url, url, timeout): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    self.logger.debug(f"Batch check failed: {url}, {e}")
                    results[url] = False
        
        return results
    
    def batch_get_speeds(self, urls, max_workers=5):
        """批量获取URL的速度"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.get_speed, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    self.logger.debug(f"Batch speed test failed: {url}, {e}")
                    results[url] = 0.00
        
        return results