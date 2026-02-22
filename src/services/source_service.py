import os
import re
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.config.config import config
from src.utils.tools import Tools

class SourceService:
    def __init__(self):
        self.tools = Tools()
        self.logger = logging.getLogger(__name__)
        self.source_dirs = {
            'download': 'source/download',
            'hotels': 'source/hotels',
            'multicast': 'source/multicast'
        }
        # 确保源目录存在
        for dir_path in self.source_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        # 数据源配置
        self.data_sources = {
            'network': [
                {'url': 'https://clun.top/lib/iptv.m3u', 'path': 'source/download/iptv.m3u', 'type': 'm3u'},
                {'url': 'https://clun.top/lib/iptv_test.m3u', 'path': 'source/download/iptv_test.m3u', 'type': 'm3u'},
                {'url': 'https://m3u.ibert.me/txt/o_s_cn_cgtn.txt', 'path': 'source/download/o_s_cn_cgtn.txt', 'type': 'txt'},
                {'url': 'https://iptv.im2k.com/bjuc.m3u', 'path': 'source/download/北京-联通-239.3.1.m3u', 'type': 'm3u'},
                {'url': 'https://iptv.im2k.com/tjuc.m3u', 'path': 'source/multicast/天津-联通-225.1.1.m3u', 'type': 'm3u'},
                {'url': 'https://raw.githubusercontent.com/qwerttvv/Beijing-IPTV/master/IPTV-Mobile-Multicast.m3u', 'path': 'source/multicast/北京-移动-228.1.1.m3u', 'type': 'm3u'},
                {'url': 'https://raw.githubusercontent.com/qwerttvv/Beijing-IPTV/master/IPTV-Unicom-Multicast.m3u', 'path': 'source/multicast/北京-联通-239.3.1.m3u', 'type': 'm3u'},
                {'url': 'https://raw.githubusercontent.com/akumajac/hebei-iptv/main/%E7%BB%84%E6%92%AD.txt', 'path': 'source/multicast/河北-电信-239.254.200.txt', 'type': 'txt'},
                {'url': 'https://raw.githubusercontent.com/Tzwcard/ChinaTelecom-GuangdongIPTV-RTP-List/master/GuangdongIPTV_rtp_hd.m3u', 'path': 'source/multicast/广东-电信-239.77.1.m3u', 'type': 'm3u'}
            ],
            'special': [
                {'name': 'sichuan_multicast', 'url': 'http://epg.51zmt.top:8000/sctvmulticast.html', 'path': 'source/multicast/四川-电信-239.93.0.txt'},
                {'name': 'internet_lives', 'url': 'http://lives.taoiptv.com/yylunbo.m3u?url=http://lives.taoiptv.com', 'path': 'source/download/yylunbo.m3u'}
            ]
        }
    
    def download_sources(self, max_workers=5):
        """下载网络数据源"""
        self.logger.info("开始下载网络数据源")
        
        success_count = 0
        fail_count = 0
        
        # 使用线程池并行下载
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {executor.submit(self._download_single_source, source): source for source in self.data_sources['network']}
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    success = future.result()
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    self.logger.error(f"下载数据源时发生异常 {source['path']}: {e}")
                    fail_count += 1
        
        self.logger.info(f"数据源下载完成: 成功 {success_count}, 失败 {fail_count}")
        return success_count, fail_count
    
    def _download_single_source(self, source):
        """下载单个数据源"""
        try:
            response = requests.get(
                source['url'], 
                headers={'User-Agent': config.crawler.get('user_agent')}, 
                timeout=30,
                stream=True
            )
            
            # 确保目录存在
            os.makedirs(os.path.dirname(source['path']), exist_ok=True)
            
            with open(source['path'], 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            self.logger.info(f"成功下载: {source['path']}")
            
            # 如果是m3u文件，转换为txt格式
            if source['type'] == 'm3u':
                txt_file = self.tools.convertToTxt(source['path'])
                if txt_file:
                    self.logger.info(f"转换为txt格式: {txt_file}")
            
            return True
        except Exception as e:
            self.logger.error(f"下载失败 {source['path']}: {e}")
            return False
    
    def fetch_sichuan_multicast(self):
        """抓取四川组播数据"""
        self.logger.info("开始抓取四川组播数据")
        source = self.data_sources['special'][0]
        sichuan_url = source['url']
        file_path = source['path']
        
        try:
            content_response = self.tools.request_body(sichuan_url)
            if content_response:
                content_response.encoding = 'utf-8'
                html_content = content_response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                table = soup.find('table', {'border': '1'})
                if table:
                    rows_even = table.find_all('tr', class_="even")
                    rows_odd = table.find_all('tr', class_="odd")
                    raw_list = rows_even + rows_odd
                    
                    result_txt = ''
                    for result_tr in raw_list:
                        td_tags = result_tr.find_all('td')
                        if len(td_tags) >= 3:
                            name = td_tags[1].text.strip()
                            ip_port = td_tags[2].text.strip()
                            if '画中画' not in name and '单音轨' not in name:
                                result_txt += f"{name},rtp://{ip_port}\n"
                    
                    # 确保目录存在
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result_txt)
                    
                    self.logger.info(f"成功抓取四川组播数据: {file_path}")
                    return True
        except Exception as e:
            self.logger.error(f"抓取四川组播数据失败: {e}")
        return False
    
    def fetch_gyssi_hotels(self, max_workers=3):
        """从gyssi.link抓取酒店源"""
        self.logger.info("开始从gyssi.link抓取酒店源")
        try:
            token_url = 'https://gyssi.link/iptv/jwt.html'
            base_url = 'https://gyssi.link/iptv/chinaiptv/'
            
            token_response = self.tools.request_body(token_url)
            if not token_response:
                self.logger.error("获取token失败")
                return []
            
            token_content = token_response.text
            token_soup = BeautifulSoup(token_content, "html.parser")
            token_element = token_soup.find(id="token")
            if not token_element:
                self.logger.error("解析token失败")
                return []
            
            token = token_element.text
            province_names = ["上海市", "云南省", "内蒙古自治区", "北京市", "吉林省", "四川省", "安徽省", "山东省", "山西省", "广东省", "广西壮族自治区", "江苏省", "江西省", "河北省", "河南省", "浙江省", "海南省", "湖北省", "湖南省", "福建省", "辽宁省", "重庆市", "陕西省", "黑龙江省"]
            
            hotel_list = []
            timeout_cnt = 0
            
            # 使用线程池并行抓取
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_province = {executor.submit(self._fetch_single_province_hotels, province, base_url, token): province for province in province_names}
                
                for future in as_completed(future_to_province):
                    province = future_to_province[future]
                    try:
                        result = future.result()
                        if result:
                            hotel_list.extend(result)
                    except (requests.Timeout, requests.RequestException) as e:
                        timeout_cnt += 1
                        self.logger.error(f"抓取酒店源超时: {province}, {e}")
                        if timeout_cnt >= 3:
                            self.logger.warning("超时次数过多，停止抓取酒店源")
                            break
                    except Exception as e:
                        self.logger.error(f"抓取酒店源异常: {province}, {e}")
            
            self.logger.info(f"gyssi酒店源抓取完成，发现 {len(hotel_list)} 个有效源")
            return hotel_list
        except Exception as e:
            self.logger.error(f"抓取gyssi酒店源失败: {e}")
            return []
    
    def _fetch_single_province_hotels(self, province, base_url, token):
        """抓取单个省份的酒店源"""
        try:
            m3u_url = base_url + province + ".m3u"
            base_file = f"source/hotels/{province}.m3u"
            
            m3u_url = m3u_url + "?token=" + token
            response = requests.get(m3u_url, timeout=15, headers={'User-Agent': config.crawler.get('user_agent')})
            
            # 确保目录存在
            os.makedirs(os.path.dirname(base_file), exist_ok=True)
            
            with open(base_file, 'wb') as file:
                file.write(response.content)
            
            file_size = os.path.getsize(base_file)
            if file_size < 1 * 1024:
                self.logger.warning(f"文件过小，可能无效: {base_file}")
                return []
            
            txt_file = self.tools.convertToTxt(base_file)
            if not txt_file:
                return []
            
            hotel_list = []
            with open(txt_file, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    match = re.search(r'http://(.*?)\/tsfile\/live', line)
                    if match:
                        ip_port = match.group(1)
                        if ':' in ip_port:
                            ip, port = ip_port.split(':', 1)
                            # 校验酒店源信息
                            channel_list = self._check_hotel_channels(ip, port)
                            count = len(channel_list)
                            if count > 3:
                                hotel_info = (ip, port, '初始采集酒店源', count, 0, datetime.now())
                                hotel_list.append(hotel_info)
                                self.logger.info(f"发现酒店源: {ip}:{port}, 频道数: {count}")
                            break
            
            return hotel_list
        except Exception as e:
            self.logger.error(f"抓取省份酒店源失败: {province}, {e}")
            return []
    
    def _check_hotel_channels(self, ip, port):
        """检查酒店源频道"""
        try:
            url = f"http://{ip}:{port}/iptv/live/1000.json?key=txiptv"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                json_data = response.json()
                if 'data' in json_data:
                    return [(item['name'], item['url']) for item in json_data['data'] if '.m3u8' in item.get('url', '') and 'http' not in item.get('url', '')]
        except Exception:
            pass
        return []
    
    def fetch_internet_lives(self):
        """抓取网络直播源"""
        self.logger.info("开始抓取网络直播源")
        source = self.data_sources['special'][1]
        file_url = source['url']
        file_path = source['path']
        
        try:
            response = requests.get(
                file_url, 
                headers={'User-Agent': config.crawler.get('user_agent')}, 
                timeout=30,
                stream=True
            )
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(file_path)
            if file_size < 3 * 1024:
                self.logger.warning(f"文件过小，可能无效: {file_path}")
                return None
            
            txt_file = self.tools.convertToTxt(file_path)
            self.logger.info(f"网络直播源抓取完成: {txt_file}")
            return txt_file
        except Exception as e:
            self.logger.error(f"抓取网络直播源失败: {e}")
            return None
    
    def get_source_status(self):
        """获取数据源状态"""
        status = {}
        
        # 检查网络数据源
        network_status = []
        for source in self.data_sources['network']:
            if os.path.exists(source['path']):
                size = os.path.getsize(source['path'])
                mtime = datetime.fromtimestamp(os.path.getmtime(source['path']))
                network_status.append({
                    'url': source['url'],
                    'path': source['path'],
                    'size': size,
                    'modified': mtime,
                    'status': 'ok'
                })
            else:
                network_status.append({
                    'url': source['url'],
                    'path': source['path'],
                    'status': 'missing'
                })
        status['network'] = network_status
        
        # 检查特殊数据源
        special_status = []
        for source in self.data_sources['special']:
            if os.path.exists(source['path']):
                size = os.path.getsize(source['path'])
                mtime = datetime.fromtimestamp(os.path.getmtime(source['path']))
                special_status.append({
                    'name': source['name'],
                    'path': source['path'],
                    'size': size,
                    'modified': mtime,
                    'status': 'ok'
                })
            else:
                special_status.append({
                    'name': source['name'],
                    'path': source['path'],
                    'status': 'missing'
                })
        status['special'] = special_status
        
        return status