# IPTV爬虫项目

## 项目概述

这是一个功能强大的IPTV爬虫项目，用于自动抓取、管理和优化IPTV直播源。项目采用模块化设计，具有高度的可扩展性和可维护性，支持多种数据源的自动抓取和整合。

### 主要功能

- **自动化数据抓取**：支持多种数据源的自动抓取和定期更新，包括网络数据源、酒店源和组播源
- **智能频道管理**：自动检测频道质量、速度和可用性，支持批量添加和管理
- **酒店源扫描**：自动扫描和发现酒店IPTV源，支持网络段扫描和质量检测
- **组播源处理**：支持组播源的解析、转换和udpxy代理管理
- **SQLite3数据库**：高效的本地数据库存储，支持自动初始化和健康检查
- **性能优化**：内置性能监控和优化机制，包括内存使用、CPU使用和函数执行时间监控
- **健康检查**：自动数据库健康检查和修复，包括连接检查、完整性检查和优化
- **并行处理**：使用线程池和连接池提高处理效率
- **错误处理**：完善的错误处理和重试机制，提高系统稳定性
- **调度管理**：智能调度器，支持自定义时间间隔的任务执行
- **数据源监控**：实时监控数据源状态和更新情况
- **视频信息解析**：使用FFmpeg解析频道的分辨率、帧率等详细信息

## 目录结构

```
iptv-spider/
├── src/                  # 源代码目录
│   ├── core/             # 核心功能模块
│   │   └── database.py   # 数据库管理
│   ├── utils/            # 工具类
│   │   ├── tools.py      # 通用工具
│   │   ├── performance.py # 性能监控
│   │   ├── retry/         # 重试机制
│   │   ├── validators/    # 验证器
│   │   └── converters/    # 转换器
│   ├── services/         # 服务层
│   │   ├── source_service.py    # 数据源服务
│   │   ├── channel_service.py    # 频道服务
│   │   ├── hotel_service.py      # 酒店服务
│   │   ├── multicast_service.py  # 组播服务
│   │   ├── scheduler.py          # 调度器
│   │   └── db_health.py          # 数据库健康检查
│   ├── models/           # 数据模型
│   ├── controllers/      # 控制器
│   ├── schemas/          # 数据模式
│   ├── middlewares/      # 中间件
│   ├── constants/        # 常量定义
│   ├── exceptions/       # 异常处理
│   ├── validators/        # 验证器
│   ├── providers/         # 数据源提供者
│   ├── parsers/           # 解析器
│   ├── generators/        # 生成器
│   └── config/           # 配置文件
│       └── config.py      # 配置管理
├── data/                 # 数据存储目录
├── logs/                 # 日志目录
├── scripts/              # 脚本文件
├── source/               # 数据源文件
│   ├── download/         # 下载的数据源
│   ├── hotels/           # 酒店源
│   └── multicast/        # 组播源
├── test_system.py        # 系统测试脚本
├── main.py               # 主程序入口
├── config.json           # 配置文件
└── README.md             # 项目文档
```

## 安装说明

### 环境要求

- Python 3.7+
- FFmpeg（用于视频信息分析）
- FFprobe（用于视频流分析）
- 依赖库：
  - requests
  - beautifulsoup4
  - sqlite3（内置）
  - psutil（用于性能监控）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/cluntop/iptv-spider.git
   cd iptv-spider
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装FFmpeg**
   - Windows：从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载并添加到系统路径
   - Linux：`apt install ffmpeg`
   - macOS：`brew install ffmpeg`

4. **配置文件**
   复制 `config.json.example` 为 `config.json` 并根据需要修改配置。

## 配置说明

### 配置文件结构

```json
{
  "database": {
    "path": "data/iptv.db"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/iptv.log"
  },
  "crawler": {
    "timeout": 30,
    "retry_count": 3,
    "sources": [
      {
        "name": "iptv_im2k",
        "url": "https://iptv.im2k.com/",
        "enabled": true
      }
    ]
  },
  "scheduler": {
    "download_interval": 24,
    "check_interval": 6,
    "cleanup_interval": 72
  },
  "validation": {
    "timeout": 15,
    "min_speed": 1.0
  }
}
```

### 主要配置项

- **database.path**：数据库文件路径
- **logging.level**：日志级别（DEBUG, INFO, WARNING, ERROR）
- **crawler.sources**：数据源配置
- **scheduler.*_interval**：调度间隔（小时）
- **validation.min_speed**：最低播放速度要求（Mbps）

## 使用方法

### 基本使用

1. **启动主程序**
   ```bash
   python main.py
   ```

2. **运行测试**
   ```bash
   python test_system.py
   ```

### 调度器模式

主程序启动后会自动进入调度器模式，按照配置的时间间隔执行以下任务：

- **每24小时**：下载数据源、抓取酒店源
- **每6小时**：检查频道速度、处理酒店源
- **每72小时**：清理无效数据、优化数据库

### 手动运行任务

可以通过修改 `main.py` 文件中的 `run_once()` 方法来手动运行特定任务。

## 核心功能说明

### 1. 数据源管理

- **网络数据源**：自动从配置的URL下载M3U文件
- **酒店源**：从gyssi.link抓取酒店IPTV源
- **组播源**：自动抓取和解析组播源
- **四川组播**：专门抓取四川电信组播数据

### 2. 频道管理

- **批量添加**：支持批量添加频道
- **速度测试**：自动测试频道播放速度
- **视频信息**：解析频道的分辨率、帧率等信息
- **分类管理**：自动匹配频道分类

### 3. 酒店源处理

- **网络扫描**：自动扫描酒店IP网段
- **质量检测**：测试酒店源的稳定性和速度
- **频道提取**：从酒店源提取有效频道

### 4. 组播处理

- **udpxy代理**：自动发现和管理udpxy代理
- **地址转换**：将组播地址转换为可访问的URL
- **质量检测**：测试组播源的播放质量

### 5. 数据库管理

- **自动初始化**：首次运行自动创建数据库结构
- **健康检查**：定期检查数据库完整性
- **优化维护**：自动执行VACUUM和ANALYZE操作
- **异常处理**：自动处理数据库锁定和连接问题

## 性能优化

### 代码优化

- **连接池**：使用requests会话和连接池减少网络开销
- **线程池**：使用并发处理提高多任务效率
- **内存管理**：优化内存使用，避免内存泄漏
- **文件I/O**：使用上下文管理器和流式读取减少I/O开销

### 数据库优化

- **索引**：为常用查询字段创建索引
- **事务**：批量操作使用事务提高效率
- **PRAGMA**：优化SQLite配置参数
- **VACUUM**：定期执行VACUUM操作回收空间

### 网络优化

- **重试机制**：自动重试失败的网络请求
- **超时设置**：合理的网络超时设置
- **缓存**：避免重复请求相同资源

## 常见问题与解决方案

### 1. 数据库连接失败

**问题**：启动时提示数据库连接失败

**解决方案**：
- 检查数据库文件权限
- 确保磁盘空间充足
- 检查config.json中的数据库路径配置

### 2. 抓取失败

**问题**：数据源抓取失败或速度慢

**解决方案**：
- 检查网络连接
- 增加crawler.timeout配置
- 检查数据源URL是否可访问

### 3. 频道质量差

**问题**：抓取的频道速度慢或不稳定

**解决方案**：
- 调整validation.min_speed配置
- 增加调度检查频率
- 检查FFmpeg是否正确安装

### 4. 内存使用高

**问题**：程序内存使用过高

**解决方案**：
- 减少并发线程数
- 调整batch_size参数
- 定期重启程序释放内存

## 监控与日志

### 日志文件

日志文件位于 `logs/iptv.log`，包含以下信息：

- 程序启动和关闭事件
- 数据源抓取状态
- 频道处理结果
- 数据库操作状态
- 性能监控数据

### 性能监控

程序内置性能监控功能，会定期输出以下信息：

- 内存使用情况
- CPU使用情况
- 函数执行时间
- 数据库大小

## 贡献指南

### 开发规范

- **代码风格**：遵循PEP 8编码规范
- **命名约定**：使用清晰的命名，避免缩写
- **文档**：为重要函数和模块添加文档字符串
- **测试**：为新功能添加测试用例

### 提交流程

1. **Fork项目**
2. **创建分支**：`git checkout -b cluntop/spider-iptv`
3. **提交修改**：`git commit -m "Add your cluntop"`
4. **推送分支**：`git push origin cluntop/spider-iptv`
5. **创建Pull Request**

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 免责声明

- 本项目仅用于学习和研究目的
- 所有数据均来自公开渠道
- 请勿用于商业用途
- 使用本项目时请遵守相关法律法规

---

**注意**：本项目依赖外部数据源，这些数据源的可用性和稳定性可能会随时变化。使用时请确保遵守相关网站的使用条款。