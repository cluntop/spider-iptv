import os
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
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
    
    def download_sources(self):
        """下载网络数据源"""
        self.logger.info("开始下载网络数据源")
        file_urls = [
            ['https://m3u.ibert.me/txt/o_s_cn_cgtn.txt', 'source/download/o_s_cn_cgtn.txt'],
            ['https://iptv.im2k.com/bjuc.m3u', 'source/download/北京-联通-239.3.1.m3u'],
            ['https://iptv.im2k.com/tjuc.m3u', 'source/multicast/天津-联通-225.1.1.m3u'],
            ['http://github.taoiptv.com/https://raw.githubusercontent.com/qwerttvv/Beijing-IPTV/master/IPTV-Mobile-Multicast.m3u', 'source/multicast/北京-移动-228.1.1.m3u'],
            ['http://github.taoiptv.com/https://raw.githubusercontent.com/qwerttvv/Beijing-IPTV/master/IPTV-Unicom-Multicast.m3u', 'source/multicast/北京-联通-239.3.1.m3u'],
            ['http://github.taoiptv.com/https://raw.githubusercontent.com/akumajac/hebei-iptv/main/%E7%BB%84%E6%92%AD.txt', 'source/multicast/河北-电信-239.254.200.txt'],
            ['http://github.taoiptv.com/https://raw.githubusercontent.com/Tzwcard/ChinaTelecom-GuangdongIPTV-RTP-List/master/GuangdongIPTV_rtp_hd.m3u', 'source/multicast/广东-电信-239.77.1.m3u']
        ]
        
        success_count = 0
        fail_count = 0
        
        for url, file_path in file_urls:
            try:
                response = requests.get(url, headers={'User-Agent': config.crawler.get('user_agent')}, timeout=30)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                self.logger.info(f"成功下载: {file_path}")
                success_count += 1
                
                # 如果是m3u文件，转换为txt格式
                if file_path.endswith('.m3u'):
                    txt_file = self.tools.convertToTxt(file_path)
                    if txt_file:
                        self.logger.info(f"转换为txt格式: {txt_file}")
            except Exception as e:
                self.logger.error(f"下载失败 {file_path}: {e}")
                fail_count += 1
        
        self.logger.info(f"数据源下载完成: 成功 {success_count}, 失败 {fail_count}")
        return success_count, fail_count
    
    def fetch_sichuan_multicast(self):
        """抓取四川组播数据"""
        self.logger.info("开始抓取四川组播数据")
        sichuan_url = 'http://epg.51zmt.top:8000/sctvmulticast.html'
        file_path = "source/multicast/四川-电信-239.93.0.txt"
        
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
                            name = td_tags[1].text
                            ip_port = td_tags[2].text
                            if '画中画' not in name and '单音轨' not in name:
                                result_txt += f"{name},rtp://{ip_port}\n"
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result_txt)
                    self.logger.info(f"成功抓取四川组播数据: {file_path}")
                    return True
        except Exception as e:
            self.logger.error(f"抓取四川组播数据失败: {e}")
        return False
    
    def fetch_gyssi_hotels(self):
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
            
            for m3u_name in province_names:
                try:
                    m3u_url = base_url + m3u_name + ".m3u"
                    base_file = f"source/hotels/{m3u_name}.m3u"
                    
                    m3u_url = m3u_url + "?token=" + token
                    response = requests.get(m3u_url, timeout=15, headers={'User-Agent': config.crawler.get('user_agent')})
                    
                    with open(base_file, 'wb') as file:
                        file.write(response.content)
                    
                    file_size = os.path.getsize(base_file)
                    if file_size < 1 * 1024:
                        self.logger.warning(f"文件过小，可能无效: {base_file}")
                        continue
                    
                    txt_file = self.tools.convertToTxt(base_file)
                    if not txt_file:
                        continue
                    
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
                except (requests.Timeout, requests.RequestException) as e:
                    timeout_cnt += 1
                    self.logger.error(f"抓取酒店源超时: {m3u_name}, {e}")
                    if timeout_cnt >= 2:
                        break
            
            self.logger.info(f"gyssi酒店源抓取完成，发现 {len(hotel_list)} 个有效源")
            return hotel_list
        except Exception as e:
            self.logger.error(f"抓取gyssi酒店源失败: {e}")
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
        file_url = 'http://lives.taoiptv.com/yylunbo.m3u?url=http://lives.taoiptv.com'
        file_path = 'source/download/yylunbo.m3u'
        
        try:
            response = requests.get(file_url, headers={'User-Agent': config.crawler.get('user_agent')}, timeout=30)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            
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

# 导入re模块
import re