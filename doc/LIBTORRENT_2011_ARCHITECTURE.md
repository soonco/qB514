# libtorrent 2.0.11 技术架构分析

## 目录结构概览

```
deps/libtorrent/2011/src/
├── ed25519/              # Ed25519 加密算法实现
├── kademlia/             # DHT (分布式哈希表) 实现
├── 核心模块 (*.cpp)      # BitTorrent 核心功能
```

## 一、核心架构层次

### 架构分层图

```
┌─────────────────────────────────────────────────────────────┐
│                     应用层 (qBittorrent)                      │
├─────────────────────────────────────────────────────────────┤
│                    公共 API 层                                │
│  session.cpp, session_handle.cpp, torrent_handle.cpp        │
├─────────────────────────────────────────────────────────────┤
│                    会话管理层                                 │
│  session_impl.cpp (核心会话实现)                             │
│  session_settings.cpp, session_params.cpp                   │
├─────────────────────────────────────────────────────────────┤
│                    种子管理层                                 │
│  torrent.cpp (核心种子逻辑)                                  │
│  torrent_info.cpp, torrent_status.cpp                       │
├─────────────────────────────────────────────────────────────┤
│                    对等节点层                                 │
│  peer_connection.cpp (基类)                                  │
│  bt_peer_connection.cpp (BitTorrent 协议)                   │
│  web_peer_connection.cpp (HTTP/FTP 种子)                    │
├─────────────────────────────────────────────────────────────┤
│                    数据传输层                                 │
│  piece_picker.cpp (片段选择策略)                             │
│  request_blocks.cpp (请求块管理)                             │
│  bandwidth_manager.cpp (带宽管理)                            │
├─────────────────────────────────────────────────────────────┤
│                    存储层                                     │
│  mmap_disk_io.cpp (内存映射 I/O)                            │
│  posix_disk_io.cpp (POSIX I/O)                              │
│  mmap_storage.cpp, posix_storage.cpp                        │
├─────────────────────────────────────────────────────────────┤
│                    网络层                                     │
│  socket_io.cpp, udp_socket.cpp                              │
│  utp_stream.cpp (uTP 协议)                                  │
│  socks5_stream.cpp, i2p_stream.cpp                          │
├─────────────────────────────────────────────────────────────┤
│                    Tracker 层                                │
│  tracker_manager.cpp                                         │
│  http_tracker_connection.cpp                                │
│  udp_tracker_connection.cpp                                 │
├─────────────────────────────────────────────────────────────┤
│                    DHT 层                                    │
│  kademlia/dht_tracker.cpp (DHT 核心)                        │
│  kademlia/routing_table.cpp (路由表)                        │
│  kademlia/node.cpp (DHT 节点)                               │
├─────────────────────────────────────────────────────────────┤
│                    工具层                                     │
│  alert.cpp (事件通知)                                        │
│  stat.cpp (统计)                                             │
│  bdecode.cpp, entry.cpp (Bencode 编解码)                    │
└─────────────────────────────────────────────────────────────┘
```

## 二、核心模块详解

### 1. 会话管理模块 (Session Management)

#### 核心文件
- **session.cpp** - 公共 API 入口，用户接口
- **session_impl.cpp** - 会话核心实现，管理所有 torrent
- **session_handle.cpp** - 会话句柄，线程安全的会话访问
- **session_settings.cpp** - 会话配置管理
- **session_params.cpp** - 会话参数
- **session_stats.cpp** - 会话统计信息

#### 主要职责
- 管理所有活动的 torrent
- 协调网络 I/O 和磁盘 I/O
- 处理全局设置和限制
- 管理 DHT、LSD、UPnP/NAT-PMP
- 事件分发和警报管理

#### 关键依赖
```
session.cpp
  ├─> session_impl.cpp (核心实现)
  ├─> mmap_disk_io.cpp (磁盘 I/O)
  ├─> posix_disk_io.cpp (POSIX I/O)
  └─> alert_manager.cpp (警报管理)
```

### 2. 种子管理模块 (Torrent Management)

#### 核心文件
- **torrent.cpp** - 种子核心逻辑 (11000+ 行)
- **torrent_handle.cpp** - 种子句柄，用户操作接口
- **torrent_info.cpp** - 种子元信息解析
- **torrent_status.cpp** - 种子状态信息
- **torrent_peer.cpp** - 对等节点信息
- **add_torrent_params.cpp** - 添加种子参数

#### 主要职责
- 管理单个 torrent 的生命周期
- 协调 peer 连接和数据传输
- 管理片段下载优先级
- 处理 tracker 通信
- 维护种子状态和统计

#### 关键依赖
```
torrent.cpp
  ├─> peer_connection.cpp (对等节点连接)
  ├─> piece_picker.cpp (片段选择)
  ├─> tracker_manager.cpp (Tracker 管理)
  ├─> stat.cpp (统计)
  └─> storage_utils.cpp (存储工具)
```

### 3. 对等节点模块 (Peer Connection)

#### 核心文件
- **peer_connection.cpp** - 对等节点连接基类
- **bt_peer_connection.cpp** - BitTorrent 协议实现
- **web_peer_connection.cpp** - HTTP/FTP 种子
- **web_connection_base.cpp** - Web 种子基类
- **http_seed_connection.cpp** - HTTP 种子
- **peer_list.cpp** - 对等节点列表管理
- **peer_connection_handle.cpp** - 连接句柄

#### 主要职责
- 实现 BitTorrent 协议
- 管理与单个 peer 的连接
- 处理消息收发
- 实现阻塞/解除阻塞算法
- 管理上传下载速率

#### 协议实现
```
peer_connection.cpp (基类)
  ├─> bt_peer_connection.cpp
  │     ├─> 握手 (handshake)
  │     ├─> 消息处理 (choke, unchoke, interested, etc.)
  │     ├─> 扩展协议 (ut_metadata, ut_pex)
  │     └─> 加密 (pe_crypto.cpp)
  │
  └─> web_peer_connection.cpp
        ├─> HTTP range 请求
        └─> URL 种子支持
```

### 4. 片段选择模块 (Piece Picker)

#### 核心文件
- **piece_picker.cpp** - 片段选择策略核心
- **request_blocks.cpp** - 块请求管理
- **hash_picker.cpp** - 哈希片段选择

#### 主要职责
- 实现片段下载策略
  - 稀有优先 (Rarest First)
  - 顺序下载 (Sequential)
  - 随机优先 (Random First)
- 管理片段优先级
- 避免重复下载
- 实现 endgame 模式

#### 策略算法
```
piece_picker.cpp
  ├─> 稀有度计算
  ├─> 优先级排序
  ├─> 部分片段管理
  └─> Endgame 模式
```

### 5. 存储模块 (Storage)

#### 核心文件
- **mmap_disk_io.cpp** - 内存映射 I/O (推荐)
- **posix_disk_io.cpp** - POSIX I/O
- **mmap_storage.cpp** - 内存映射存储
- **posix_storage.cpp** - POSIX 存储
- **disabled_disk_io.cpp** - 禁用磁盘 I/O
- **disk_buffer_pool.cpp** - 磁盘缓冲池
- **disk_job_pool.cpp** - 磁盘任务池
- **part_file.cpp** - 部分文件管理
- **storage_utils.cpp** - 存储工具

#### 主要职责
- 文件读写操作
- 缓冲管理
- 哈希校验
- 文件分配和移动
- 支持多文件 torrent

#### I/O 架构
```
磁盘 I/O 层
  ├─> mmap_disk_io.cpp (推荐)
  │     ├─> 内存映射文件
  │     ├─> 零拷贝
  │     └─> 高性能
  │
  └─> posix_disk_io.cpp
        ├─> 传统文件 I/O
        ├─> 缓冲管理
        └─> 跨平台兼容
```

### 6. 网络模块 (Network)

#### 核心文件
- **socket_io.cpp** - Socket I/O 基础
- **udp_socket.cpp** - UDP Socket
- **utp_stream.cpp** - uTP 协议实现
- **utp_socket_manager.cpp** - uTP Socket 管理
- **socks5_stream.cpp** - SOCKS5 代理
- **i2p_stream.cpp** - I2P 匿名网络
- **proxy_base.cpp** - 代理基类
- **ssl.cpp** - SSL/TLS 支持

#### 主要职责
- TCP/UDP Socket 管理
- uTP 协议实现
- 代理支持 (SOCKS5, HTTP)
- SSL/TLS 加密
- I2P 匿名网络

#### 网络协议栈
```
应用层
  ├─> BitTorrent 协议
  └─> HTTP/HTTPS

传输层
  ├─> TCP (传统)
  ├─> uTP (uTorrent Transport Protocol)
  └─> UDP (DHT, Tracker)

代理层
  ├─> SOCKS5
  ├─> HTTP Proxy
  └─> I2P
```

### 7. Tracker 模块

#### 核心文件
- **tracker_manager.cpp** - Tracker 管理器
- **http_tracker_connection.cpp** - HTTP Tracker
- **udp_tracker_connection.cpp** - UDP Tracker
- **announce_entry.cpp** - Tracker 条目

#### 主要职责
- 管理 tracker 列表
- 发送 announce 请求
- 处理 tracker 响应
- 获取 peer 列表
- Scrape 请求

#### Tracker 通信流程
```
tracker_manager.cpp
  ├─> http_tracker_connection.cpp
  │     ├─> 构建 announce URL
  │     ├─> 发送 HTTP GET
  │     ├─> 解析 Bencode 响应
  │     └─> 提取 peer 列表
  │
  └─> udp_tracker_connection.cpp
        ├─> 连接请求
        ├─> Announce 请求
        ├─> Scrape 请求
        └─> 二进制协议解析
```

### 8. DHT 模块 (Kademlia)

#### 核心文件 (kademlia/ 目录)
- **dht_tracker.cpp** - DHT Tracker 实现
- **node.cpp** - DHT 节点
- **routing_table.cpp** - Kademlia 路由表
- **rpc_manager.cpp** - RPC 管理
- **find_data.cpp** - 查找数据
- **get_peers.cpp** - 获取 peer
- **get_item.cpp** - 获取数据项
- **put_data.cpp** - 存储数据
- **sample_infohashes.cpp** - 采样 infohash
- **node_id.cpp** - 节点 ID
- **node_entry.cpp** - 节点条目
- **dht_storage.cpp** - DHT 存储
- **dht_settings.cpp** - DHT 设置

#### 主要职责
- 实现 Kademlia DHT 协议
- 无 tracker 的 peer 发现
- 分布式数据存储
- BEP 44 可变/不可变数据

#### DHT 架构
```
dht_tracker.cpp (入口)
  ├─> node.cpp (DHT 节点)
  │     ├─> routing_table.cpp (路由表)
  │     │     ├─> K-桶算法
  │     │     └─> 节点管理
  │     │
  │     ├─> rpc_manager.cpp (RPC)
  │     │     ├─> ping
  │     │     ├─> find_node
  │     │     ├─> get_peers
  │     │     ├─> announce_peer
  │     │     ├─> get (BEP 44)
  │     │     └─> put (BEP 44)
  │     │
  │     └─> traversal_algorithm.cpp
  │           ├─> find_data.cpp
  │           ├─> get_peers.cpp
  │           ├─> get_item.cpp
  │           └─> refresh.cpp
  │
  └─> dht_storage.cpp (数据存储)
```

### 9. 扩展协议模块

#### 核心文件
- **ut_metadata.cpp** - BEP 9: 元数据交换
- **ut_pex.cpp** - BEP 11: Peer Exchange
- **smart_ban.cpp** - 智能封禁

#### 主要职责
- ut_metadata: 无 .torrent 文件下载
- ut_pex: 快速 peer 发现
- smart_ban: 检测恶意 peer

### 10. 加密模块

#### 核心文件
- **pe_crypto.cpp** - 协议加密 (BEP 3)
- **ssl.cpp** - SSL/TLS
- **ed25519/** - Ed25519 签名算法
  - keypair.cpp - 密钥对生成
  - sign.cpp - 签名
  - verify.cpp - 验证
  - sha512.cpp - SHA-512 哈希

#### 主要职责
- 协议加密 (MSE/PE)
- SSL/TLS 支持
- Ed25519 数字签名 (BEP 44)

### 11. 编解码模块

#### 核心文件
- **bdecode.cpp** - Bencode 解码
- **entry.cpp** - Bencode 数据结构
- **create_torrent.cpp** - 创建 .torrent 文件
- **load_torrent.cpp** - 加载 .torrent 文件
- **magnet_uri.cpp** - 磁力链接解析

#### 主要职责
- Bencode 编解码
- .torrent 文件处理
- 磁力链接支持

### 12. 工具模块

#### 核心文件
- **alert.cpp** - 事件警报系统
- **alert_manager.cpp** - 警报管理
- **stat.cpp** - 统计信息
- **bandwidth_manager.cpp** - 带宽管理
- **bandwidth_limit.cpp** - 带宽限制
- **choker.cpp** - 阻塞算法
- **ip_filter.cpp** - IP 过滤
- **ip_voter.cpp** - 外部 IP 投票
- **bloom_filter.cpp** - 布隆过滤器
- **random.cpp** - 随机数生成
- **time.cpp** - 时间工具
- **file.cpp** - 文件操作
- **path.cpp** - 路径处理

## 三、关键数据流

### 1. 下载数据流

```
1. 用户添加 torrent
   session::add_torrent()
     ↓
2. 创建 torrent 对象
   session_impl::add_torrent()
     ↓
3. 连接 tracker/DHT
   tracker_manager::announce()
   dht_tracker::get_peers()
     ↓
4. 获取 peer 列表
   peer_list::add_peer()
     ↓
5. 建立 peer 连接
   bt_peer_connection::connect()
     ↓
6. 握手和交换 bitfield
   bt_peer_connection::on_handshake()
     ↓
7. 选择要下载的片段
   piece_picker::pick_pieces()
     ↓
8. 请求数据块
   peer_connection::request_block()
     ↓
9. 接收数据
   peer_connection::incoming_piece()
     ↓
10. 写入磁盘
    mmap_disk_io::async_write()
     ↓
11. 哈希校验
    torrent::on_piece_verified()
     ↓
12. 更新统计
    stat::received_bytes()
    torrent::m_total_downloaded++
```

### 2. 上传数据流

```
1. Peer 请求数据块
   peer_connection::incoming_request()
     ↓
2. 检查阻塞状态
   choker::unchoke_one()
     ↓
3. 从磁盘读取
   mmap_disk_io::async_read()
     ↓
4. 发送数据
   peer_connection::send_block()
     ↓
5. 更新统计
   stat::sent_bytes()
   torrent::m_total_uploaded++
```

### 3. Tracker Announce 流程

```
1. 触发 announce
   torrent::announce_with_tracker()
     ↓
2. 构建请求
   http_tracker_connection::start()
     ↓
3. 添加参数
   - info_hash
   - peer_id
   - uploaded (m_total_uploaded)
   - downloaded (m_total_downloaded)
   - left
   - event
     ↓
4. 发送 HTTP 请求
   http_connection::get()
     ↓
5. 接收响应
   http_tracker_connection::on_response()
     ↓
6. 解析 peer 列表
   bdecode::decode()
     ↓
7. 添加 peer
   peer_list::add_peer()
```

## 四、模块依赖关系图

```
┌─────────────────────────────────────────────────────────┐
│                      session.cpp                         │
│                   (公共 API 入口)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  session_impl.cpp                        │
│              (核心会话实现，协调器)                       │
└─┬─────────┬─────────┬─────────┬─────────┬──────────────┘
  │         │         │         │         │
  │         │         │         │         │
  ▼         ▼         ▼         ▼         ▼
┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌──────┐
│tor │  │dht │  │tra │  │disk│  │alert │
│rent│  │_tr │  │cker│  │_io │  │_mgr  │
└─┬──┘  └────┘  └────┘  └────┘  └──────┘
  │
  ├─> peer_connection (对等节点)
  ├─> piece_picker (片段选择)
  ├─> tracker_manager (Tracker)
  └─> storage (存储)
```

## 五、文件分类汇总

### 核心管理 (Core Management)
```
session.cpp, session_impl.cpp, session_handle.cpp
session_settings.cpp, session_params.cpp, session_stats.cpp
torrent.cpp, torrent_handle.cpp, torrent_info.cpp
torrent_status.cpp, torrent_peer.cpp
```

### 网络通信 (Network)
```
peer_connection.cpp, bt_peer_connection.cpp
web_peer_connection.cpp, http_seed_connection.cpp
socket_io.cpp, udp_socket.cpp
utp_stream.cpp, utp_socket_manager.cpp
socks5_stream.cpp, i2p_stream.cpp
http_connection.cpp, http_parser.cpp
```

### Tracker (Tracker)
```
tracker_manager.cpp
http_tracker_connection.cpp
udp_tracker_connection.cpp
announce_entry.cpp
```

### DHT (Distributed Hash Table)
```
kademlia/dht_tracker.cpp
kademlia/node.cpp
kademlia/routing_table.cpp
kademlia/rpc_manager.cpp
kademlia/get_peers.cpp
kademlia/find_data.cpp
... (其他 kademlia/ 文件)
```

### 存储 (Storage)
```
mmap_disk_io.cpp, posix_disk_io.cpp
mmap_storage.cpp, posix_storage.cpp
disk_buffer_pool.cpp, disk_job_pool.cpp
part_file.cpp, storage_utils.cpp
file.cpp, file_storage.cpp
```

### 数据处理 (Data Processing)
```
piece_picker.cpp, request_blocks.cpp
hash_picker.cpp, merkle_tree.cpp
bdecode.cpp, entry.cpp
create_torrent.cpp, load_torrent.cpp
```

### 扩展协议 (Extensions)
```
ut_metadata.cpp, ut_pex.cpp
smart_ban.cpp
```

### 加密 (Cryptography)
```
pe_crypto.cpp, ssl.cpp
ed25519/*.cpp (Ed25519 算法)
hasher.cpp, sha1.cpp, sha256.cpp
```

### 网络服务 (Network Services)
```
lsd.cpp (Local Service Discovery)
natpmp.cpp (NAT-PMP)
upnp.cpp (UPnP)
```

### 工具 (Utilities)
```
alert.cpp, alert_manager.cpp
stat.cpp, bandwidth_manager.cpp
choker.cpp, ip_filter.cpp
random.cpp, time.cpp
escape_string.cpp, hex.cpp
```

## 六、技术特性

### 1. 性能优化
- **内存映射 I/O**: mmap_disk_io.cpp 提供零拷贝高性能
- **uTP 协议**: 减少延迟，友好带宽
- **智能片段选择**: 稀有优先算法
- **带宽管理**: 精确的上传下载控制

### 2. 协议支持
- **BitTorrent v1**: 标准协议
- **BitTorrent v2**: Merkle 树，更好的哈希
- **DHT**: 无 tracker 支持
- **PEX**: Peer 交换
- **uTP**: 微传输协议
- **加密**: MSE/PE 协议加密

### 3. 扩展功能
- **磁力链接**: 无需 .torrent 文件
- **Web 种子**: HTTP/FTP 下载
- **I2P**: 匿名网络
- **代理**: SOCKS5, HTTP
- **SSL/TLS**: 安全连接

### 4. 平台支持
- **跨平台**: Windows, Linux, macOS, BSD
- **多种 I/O**: mmap, POSIX
- **灵活配置**: 丰富的设置选项

## 七、代码规模统计

| 模块 | 文件数 | 主要文件行数 |
|------|--------|-------------|
| 核心管理 | 15 | session_impl.cpp (~8000 行) |
| 种子管理 | 8 | torrent.cpp (~11000 行) |
| 对等节点 | 10 | peer_connection.cpp (~5000 行) |
| 存储 | 15 | mmap_disk_io.cpp (~2000 行) |
| 网络 | 12 | utp_stream.cpp (~2000 行) |
| Tracker | 4 | tracker_manager.cpp (~1000 行) |
| DHT | 18 | dht_tracker.cpp (~2000 行) |
| 工具 | 30+ | 各文件 100-1000 行 |

**总计**: 约 150+ 个 .cpp 文件，超过 100,000 行代码

## 八、总结

libtorrent 2.0.11 是一个**高度模块化**、**功能完整**的 BitTorrent 库：

### 核心优势
1. ✅ **完整的协议支持**: BitTorrent v1/v2, DHT, PEX, uTP
2. ✅ **高性能**: 内存映射 I/O, 零拷贝, 智能算法
3. ✅ **灵活性**: 多种 I/O 后端, 丰富配置
4. ✅ **安全性**: 加密支持, IP 过滤, 智能封禁
5. ✅ **可扩展**: 插件系统, 扩展协议

### 架构特点
- **分层清晰**: 从 API 到底层网络/存储
- **职责明确**: 每个模块有清晰的边界
- **高内聚低耦合**: 模块间通过接口交互
- **事件驱动**: 基于 alert 的异步通知

### 适用场景
- P2P 文件分享应用 (如 qBittorrent)
- 大规模内容分发
- 去中心化存储
- 任何需要 BitTorrent 协议的场景

这个架构设计使得 libtorrent 成为业界最成熟、最可靠的 BitTorrent 库之一。
