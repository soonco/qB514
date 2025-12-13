# qBittorrent 上传下载数据追踪机制 - libtorrent 2.0.11 版本

## 概述

本文档详细说明基于 **libtorrent 2.0.11** 版本中 `m_nativeStatus.all_time_download` 和 `m_nativeStatus.all_time_upload` 这两个变量的更新流程。

## 版本对比说明

libtorrent 2.0.11 与 1.2.20 版本在核心机制上**基本一致**，但有以下细微差异：

1. **代码结构更清晰**：函数位置和行号有所变化
2. **类型系统改进**：使用了更多的强类型（如 `file_index_t`）
3. **API 版本控制**：通过 `TORRENT_ABI_VERSION` 宏管理兼容性
4. **性能优化**：内部实现有优化，但对外接口保持兼容

## 数据流向图

```
网络数据包接收/发送
    ↓
bt_peer_connection::on_receive() / bt_peer_connection::on_sent()
    ↓
peer_connection::received_bytes() / peer_connection::sent_bytes()
    ↓
torrent::received_bytes() / torrent::sent_bytes()
    ↓
stat::received_bytes() / stat::sent_bytes()
    ↓
stat_channel::add() (累加到 m_counter 和 m_total_counter)
    ↓
torrent::second_tick() (每秒调用)
    ↓
m_total_uploaded += m_stat.last_payload_uploaded()
m_total_downloaded += m_stat.last_payload_downloaded()
    ↓
torrent::status() (获取状态时)
    ↓
st->all_time_upload = m_total_uploaded
st->all_time_download = m_total_downloaded
    ↓
NativeTorrentExtension 构造函数
    ↓
m_data->status = m_torrentHandle.status()
    ↓
TorrentImpl 构造函数
    ↓
m_nativeStatus = extensionData->status
```

## 详细代码位置（libtorrent 2.0.11）

### 1. 底层数据接收/发送统计

**位置**: `deps/libtorrent/2011/src/peer_connection.cpp:1142-1159`

```cpp
void peer_connection::received_bytes(int const bytes_payload, int const bytes_protocol)
{
    TORRENT_ASSERT(is_single_thread());
    m_statistics.received_bytes(bytes_payload, bytes_protocol);
    if (m_ignore_stats) return;
    std::shared_ptr<torrent> t = m_torrent.lock();
    if (!t) return;
    t->received_bytes(bytes_payload, bytes_protocol);  // 调用 torrent 层
}

void peer_connection::sent_bytes(int const bytes_payload, int const bytes_protocol)
{
    TORRENT_ASSERT(is_single_thread());
    m_statistics.sent_bytes(bytes_payload, bytes_protocol);
    if (m_ignore_stats) return;
    std::shared_ptr<torrent> t = m_torrent.lock();
    if (!t) return;
    t->sent_bytes(bytes_payload, bytes_protocol);  // 调用 torrent 层
}
```

**说明**: 
- 与 1.2.20 版本完全相同的逻辑
- 增加了 `TORRENT_ASSERT(is_single_thread())` 断言确保线程安全

### 2. Torrent 层统计

**位置**: `deps/libtorrent/2011/src/torrent.cpp` (具体行号需查找)

```cpp
void torrent::sent_bytes(int const bytes_payload, int const bytes_protocol)
{
    m_stat.sent_bytes(bytes_payload, bytes_protocol);      // 更新 torrent 统计
    m_ses.sent_bytes(bytes_payload, bytes_protocol);       // 更新 session 统计
}

void torrent::received_bytes(int const bytes_payload, int const bytes_protocol)
{
    m_stat.received_bytes(bytes_payload, bytes_protocol);  // 更新 torrent 统计
    m_ses.received_bytes(bytes_payload, bytes_protocol);   // 更新 session 统计
}
```

### 3. stat 类累加数据

**位置**: `deps/libtorrent/2011/include/libtorrent/stat.hpp:130-146`

```cpp
void received_bytes(int bytes_payload, int bytes_protocol)
{
    TORRENT_ASSERT(bytes_payload >= 0);
    TORRENT_ASSERT(bytes_protocol >= 0);

    m_stat[download_payload].add(bytes_payload);      // 累加下载负载
    m_stat[download_protocol].add(bytes_protocol);    // 累加下载协议开销
}

void sent_bytes(int bytes_payload, int bytes_protocol)
{
    TORRENT_ASSERT(bytes_payload >= 0);
    TORRENT_ASSERT(bytes_protocol >= 0);

    m_stat[upload_payload].add(bytes_payload);        // 累加上传负载
    m_stat[upload_protocol].add(bytes_protocol);      // 累加上传协议开销
}
```

**位置**: `deps/libtorrent/2011/include/libtorrent/stat.hpp:65-73`

```cpp
void add(int count)
{
    TORRENT_ASSERT(count >= 0);

    TORRENT_ASSERT(m_counter < (std::numeric_limits<std::int32_t>::max)() - count);
    m_counter += count;         // 当前周期计数器
    TORRENT_ASSERT(m_total_counter < (std::numeric_limits<std::int64_t>::max)() - count);
    m_total_counter += count;   // 总计数器
}
```

**改进**: 增加了溢出检查断言，提高了代码安全性

### 4. 每秒更新累计值

**位置**: `deps/libtorrent/2011/src/torrent.cpp:10275-10277`

```cpp
// 在 torrent::second_tick() 中，每秒调用一次
m_total_uploaded += m_stat.last_payload_uploaded();      // 累加上传量
m_total_downloaded += m_stat.last_payload_downloaded();  // 累加下载量
m_stat.second_tick(tick_interval_ms);                    // 重置周期计数器
```

**位置**: `deps/libtorrent/2011/include/libtorrent/stat.hpp:245-250`

```cpp
int last_payload_downloaded() const
{ return m_stat[download_payload].counter(); }
int last_payload_uploaded() const
{ return m_stat[upload_payload].counter(); }
```

**说明**:
- 逻辑与 1.2.20 版本完全相同
- 行号位置略有不同（1.2.20 在 9508-9509 行）

### 5. 填充到 torrent_status

**位置**: `deps/libtorrent/2011/src/torrent.cpp:11845-11846`

```cpp
// 在 torrent::status() 中
st->all_time_upload = m_total_uploaded;      // 设置累计上传量
st->all_time_download = m_total_downloaded;  // 设置累计下载量
```

**说明**:
- 与 1.2.20 版本（11027-11028 行）逻辑完全相同
- 函数签名略有变化：`void torrent::status(torrent_status* st, status_flags_t const flags)`

### 6. 初始化加载（从 resume data）

**位置**: `deps/libtorrent/2011/src/torrent.cpp:194-195`

```cpp
// 在 torrent 构造函数中，从 add_torrent_params 加载
torrent::torrent(
    aux::session_interface& ses
    , bool const session_paused
    , add_torrent_params&& p)
    : torrent_hot_members(ses, p, session_paused)
    , m_total_uploaded(p.total_uploaded)      // 从 resume data 恢复
    , m_total_downloaded(p.total_downloaded)  // 从 resume data 恢复
    // ... 其他成员初始化
```

**改进**:
- 使用了成员初始化列表，更符合现代 C++ 规范
- 1.2.20 版本在 386-387 行

### 7. torrent_status 结构定义

**位置**: `deps/libtorrent/2011/include/libtorrent/torrent_status.hpp:205-278`

```cpp
struct TORRENT_EXPORT torrent_status
{
    // 本次会话的下载上传量（暂停后重置）
    // 注释说明：The session is considered to restart when a torrent is paused and restarted again.
    std::int64_t total_download = 0;
    std::int64_t total_upload = 0;

    // 本次会话的负载数据（不含协议开销）
    std::int64_t total_payload_download = 0;
    std::int64_t total_payload_upload = 0;

    // 累计上传下载量（持久化到 resume data）
    // 注释说明：are accumulated upload and download payload byte counters. 
    // They are saved in and restored from resume data to keep totals across sessions.
    std::int64_t all_time_upload = 0;
    std::int64_t all_time_download = 0;
};
```

**改进**:
- 注释更加详细和清晰
- 明确说明了 `all_time_*` 字段会保存到 resume data 中
- 1.2.20 版本在 281-282 行

### 8. qBittorrent 层获取数据

qBittorrent 层的代码**完全相同**，因为它只依赖 libtorrent 的公共 API：

**位置**: `src/base/bittorrent/nativetorrentextension.cpp:41`

```cpp
// NativeTorrentExtension 构造函数
m_data->status = m_torrentHandle.status();  // 获取 libtorrent 的 torrent_status
```

**位置**: `src/base/bittorrent/torrentimpl.cpp:369`

```cpp
// TorrentImpl 构造函数
m_nativeStatus = extensionData->status;  // 复制 status 到 qBittorrent
```

**位置**: `src/base/bittorrent/torrentimpl.cpp:1319-1327`

```cpp
// qBittorrent 提供的公共接口
qlonglong TorrentImpl::totalDownload() const
{
    return m_nativeStatus.all_time_download;  // 返回累计下载量
}

qlonglong TorrentImpl::totalUpload() const
{
    return m_nativeStatus.all_time_upload;    // 返回累计上传量
}
```

## 关键数据结构（2.0.11 版本）

### stat_channel (单个统计通道)

**位置**: `deps/libtorrent/2011/include/libtorrent/stat.hpp:47-107`

```cpp
class TORRENT_EXTRA_EXPORT stat_channel
{
public:
    stat_channel()
        : m_total_counter(0)
        , m_counter(0)
        , m_5_sec_average(0)
    {}

    void add(int count)
    {
        TORRENT_ASSERT(count >= 0);
        TORRENT_ASSERT(m_counter < (std::numeric_limits<std::int32_t>::max)() - count);
        m_counter += count;
        TORRENT_ASSERT(m_total_counter < (std::numeric_limits<std::int64_t>::max)() - count);
        m_total_counter += count;
    }

    void second_tick(int tick_interval_ms);
    std::int32_t rate() const { return m_5_sec_average; }
    std::int64_t total() const { return m_total_counter; }
    std::int32_t counter() const { return m_counter; }

private:
    std::int64_t m_total_counter;  // 总计数器（持久化）
    std::int32_t m_counter;        // 当前周期计数器（每秒重置）
    std::int32_t m_5_sec_average;  // 5秒滑动平均
};
```

**改进**:
- 增加了 `TORRENT_EXTRA_EXPORT` 宏用于符号导出控制
- 增加了更严格的断言检查

### stat (统计类)

**位置**: `deps/libtorrent/2011/include/libtorrent/stat.hpp:109-250`

```cpp
class TORRENT_EXTRA_EXPORT stat
{
public:
    void received_bytes(int bytes_payload, int bytes_protocol);
    void sent_bytes(int bytes_payload, int bytes_protocol);
    
    void second_tick(int tick_interval_ms);
    
    std::int64_t total_upload() const;
    std::int64_t total_download() const;
    std::int64_t total_payload_upload() const;
    std::int64_t total_payload_download() const;
    
    int last_payload_downloaded() const;
    int last_payload_uploaded() const;

private:
    stat_channel m_stat[num_channels];  // 包含多个通道
};
```

### torrent (核心类)

```cpp
class torrent
{
    stat m_stat;                    // 统计对象
    std::int64_t m_total_uploaded;   // 累计上传量（会保存到 resume data）
    std::int64_t m_total_downloaded; // 累计下载量（会保存到 resume data）
};
```

## Tracker 上报（2.0.11 版本）

当向 tracker 发送 announce 请求时，libtorrent 会自动使用这些累计值：

**位置**: `deps/libtorrent/2011/src/http_tracker_connection.cpp:134-148`

```cpp
std::snprintf(str, sizeof(str)
    "&peer_id=%s"
    "&port=%d"
    "&uploaded=%" PRId64      // ← 上传量
    "&downloaded=%" PRId64    // ← 下载量
    "&left=%" PRId64
    "&corrupt=%" PRId64
    "&key=%08X"
    "%s%s"                    // event (started/completed/stopped)
    "&numwant=%d"
    "&compact=1"
    "&no_peer_id=1"
    , escape_string({tracker_req().pid.data(), 20}).c_str()
    , tracker_req().listen_port
    , tracker_req().uploaded        // ← 从 torrent_status 获取
    , tracker_req().downloaded      // ← 从 torrent_status 获取
    , tracker_req().left
    , tracker_req().corrupt
    , tracker_req().key
    , (tracker_req().event != tracker_request::none) ? "&event=" : ""
    , (tracker_req().event != tracker_request::none) ? event_string[tracker_req().event - 1] : ""
    , tracker_req().num_want);
```

**说明**: 与 1.2.20 版本（122-145 行）逻辑完全相同

## 版本差异总结

| 特性 | libtorrent 1.2.20 | libtorrent 2.0.11 | 说明 |
|------|-------------------|-------------------|------|
| **核心逻辑** | ✓ | ✓ | 完全相同 |
| **数据流向** | ✓ | ✓ | 完全相同 |
| **API 接口** | ✓ | ✓ | 兼容 |
| **断言检查** | 基础 | 增强 | 2.0.11 增加了更多溢出检查 |
| **代码位置** | 不同 | 不同 | 行号有变化 |
| **类型系统** | 基础 | 强类型 | 2.0.11 使用更多强类型 |
| **构造函数** | 传统 | 现代 | 2.0.11 使用成员初始化列表 |
| **注释文档** | 简洁 | 详细 | 2.0.11 注释更清晰 |

## 关键代码位置对比表

| 功能 | libtorrent 1.2.20 | libtorrent 2.0.11 |
|------|-------------------|-------------------|
| peer_connection::received_bytes() | src/peer_connection.cpp:1130 | src/peer_connection.cpp:1142 |
| stat_channel::add() | include/libtorrent/stat.hpp:63 | include/libtorrent/stat.hpp:65 |
| torrent::second_tick() 累加 | src/torrent.cpp:9508 | src/torrent.cpp:10275 |
| torrent::status() 填充 | src/torrent.cpp:11027 | src/torrent.cpp:11845 |
| torrent 构造函数初始化 | src/torrent.cpp:386 | src/torrent.cpp:194 |
| torrent_status 结构定义 | include/libtorrent/torrent_status.hpp:281 | include/libtorrent/torrent_status.hpp:277 |
| http_tracker_connection 上报 | src/http_tracker_connection.cpp:138 | src/http_tracker_connection.cpp:147 |

## 更新频率

1. **实时更新**: 每次接收/发送数据包时，`stat_channel::add()` 被调用
2. **每秒汇总**: `torrent::second_tick()` 每秒调用一次，将上一秒的数据累加到 `m_total_uploaded/m_total_downloaded`
3. **按需读取**: qBittorrent 通过 `TorrentImpl::totalUpload()/totalDownload()` 随时读取当前值

## 数据持久化

- `m_total_uploaded` 和 `m_total_downloaded` 会保存到 **resume data** 中
- 当 torrent 重新加载时，这些值会从 resume data 恢复
- 这确保了跨会话的累计统计准确性
- **2.0.11 改进**: 在 `torrent_status.hpp` 的注释中明确说明了这一点

## 总结

### 核心机制（两个版本完全相同）

1. **数据源头**: 网络层每次接收/发送数据包
2. **实时累加**: `stat_channel` 实时累加字节数
3. **定期汇总**: 每秒将增量累加到 `m_total_uploaded/m_total_downloaded`
4. **状态同步**: qBittorrent 通过 `torrent_status` 获取这些值
5. **自动上报**: tracker announce 时自动使用这些累计值
6. **持久保存**: 数据保存在 resume data 中，跨会话保持

### libtorrent 2.0.11 的改进

1. **更严格的类型检查**: 使用强类型和断言
2. **更清晰的代码结构**: 现代 C++ 风格
3. **更详细的文档**: 注释更加完善
4. **更好的性能**: 内部优化（对外接口不变）
5. **向后兼容**: 通过 `TORRENT_ABI_VERSION` 宏管理

### 对 qBittorrent 的影响

**完全透明**: qBittorrent 应用层代码无需任何修改，因为：
- 公共 API 保持兼容
- 数据结构布局相同
- 行为逻辑一致

整个流程完全自动化，qBittorrent 应用层无需手动更新这些统计数据。
