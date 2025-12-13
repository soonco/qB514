# qBittorrent 上传下载数据追踪机制

## 概述

本文档详细说明 `m_nativeStatus.all_time_download` 和 `m_nativeStatus.all_time_upload` 这两个变量在代码中的更新流程。

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

## 详细代码位置

### 1. 底层数据接收/发送统计

**位置**: `deps/libtorrent/1220/src/peer_connection.cpp:1130-1145`

```cpp
void peer_connection::received_bytes(int const bytes_payload, int const bytes_protocol)
{
    m_statistics.received_bytes(bytes_payload, bytes_protocol);
    if (m_ignore_stats) return;
    std::shared_ptr<torrent> t = m_torrent.lock();
    if (!t) return;
    t->received_bytes(bytes_payload, bytes_protocol);  // 调用 torrent 层
}

void peer_connection::sent_bytes(int const bytes_payload, int const bytes_protocol)
{
    m_statistics.sent_bytes(bytes_payload, bytes_protocol);
    if (m_ignore_stats) return;
    std::shared_ptr<torrent> t = m_torrent.lock();
    if (!t) return;
    t->sent_bytes(bytes_payload, bytes_protocol);  // 调用 torrent 层
}
```

**说明**: 
- `bytes_payload`: 实际数据负载字节数
- `bytes_protocol`: 协议开销字节数
- 这些函数在每次接收/发送数据包时被调用

### 2. Torrent 层统计

**位置**: `deps/libtorrent/1220/src/torrent.cpp:9757-9767`

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

**位置**: `deps/libtorrent/1220/include/libtorrent/stat.hpp:128-144`

```cpp
void received_bytes(int bytes_payload, int bytes_protocol)
{
    m_stat[download_payload].add(bytes_payload);      // 累加下载负载
    m_stat[download_protocol].add(bytes_protocol);    // 累加下载协议开销
}

void sent_bytes(int bytes_payload, int bytes_protocol)
{
    m_stat[upload_payload].add(bytes_payload);        // 累加上传负载
    m_stat[upload_protocol].add(bytes_protocol);      // 累加上传协议开销
}
```

**位置**: `deps/libtorrent/1220/include/libtorrent/stat.hpp:63-71`

```cpp
void add(int count)
{
    m_counter += count;         // 当前周期计数器
    m_total_counter += count;   // 总计数器
}
```

### 4. 每秒更新累计值

**位置**: `deps/libtorrent/1220/src/torrent.cpp:9508-9509`

```cpp
// 在 torrent::second_tick() 中，每秒调用一次
m_total_uploaded += m_stat.last_payload_uploaded();      // 累加上传量
m_total_downloaded += m_stat.last_payload_downloaded();  // 累加下载量
m_stat.second_tick(tick_interval_ms);                    // 重置周期计数器
```

**说明**:
- `last_payload_uploaded()` 返回 `m_stat[upload_payload].counter()`
- `last_payload_downloaded()` 返回 `m_stat[download_payload].counter()`
- 这些是上一秒的累计值

### 5. 填充到 torrent_status

**位置**: `deps/libtorrent/1220/src/torrent.cpp:11027-11028`

```cpp
// 在 torrent::status() 中
st->all_time_upload = m_total_uploaded;      // 设置累计上传量
st->all_time_download = m_total_downloaded;  // 设置累计下载量
```

### 6. 初始化加载（从 resume data）

**位置**: `deps/libtorrent/1220/src/torrent.cpp:386-387`

```cpp
// 在 torrent 构造函数中，从 add_torrent_params 加载
m_total_uploaded = p.total_uploaded;      // 从 resume data 恢复
m_total_downloaded = p.total_downloaded;  // 从 resume data 恢复
```

### 7. qBittorrent 层获取数据

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

## 关键数据结构

### stat_channel (单个统计通道)

```cpp
class stat_channel
{
    std::int64_t m_total_counter;  // 总计数器（持久化）
    std::int32_t m_counter;        // 当前周期计数器（每秒重置）
    std::int32_t m_5_sec_average;  // 5秒滑动平均
};
```

### stat (统计类)

```cpp
class stat
{
    stat_channel m_stat[num_channels];  // 包含多个通道：
                                        // - upload_payload (上传负载)
                                        // - upload_protocol (上传协议)
                                        // - download_payload (下载负载)
                                        // - download_protocol (下载协议)
                                        // - upload_ip_protocol
                                        // - download_ip_protocol
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

## 更新频率

1. **实时更新**: 每次接收/发送数据包时，`stat_channel::add()` 被调用
2. **每秒汇总**: `torrent::second_tick()` 每秒调用一次，将上一秒的数据累加到 `m_total_uploaded/m_total_downloaded`
3. **按需读取**: qBittorrent 通过 `TorrentImpl::totalUpload()/totalDownload()` 随时读取当前值

## 数据持久化

- `m_total_uploaded` 和 `m_total_downloaded` 会保存到 **resume data** 中
- 当 torrent 重新加载时，这些值会从 resume data 恢复
- 这确保了跨会话的累计统计准确性

## Tracker 上报

当向 tracker 发送 announce 请求时，libtorrent 会自动使用这些累计值：

**位置**: `deps/libtorrent/1220/src/http_tracker_connection.cpp:138-139`

```cpp
"&uploaded=%" PRId64
"&downloaded=%" PRId64
, tracker_req().uploaded      // 来自 m_total_uploaded
, tracker_req().downloaded    // 来自 m_total_downloaded
```

## 总结

1. **数据源头**: 网络层每次接收/发送数据包
2. **实时累加**: `stat_channel` 实时累加字节数
3. **定期汇总**: 每秒将增量累加到 `m_total_uploaded/m_total_downloaded`
4. **状态同步**: qBittorrent 通过 `torrent_status` 获取这些值
5. **自动上报**: tracker announce 时自动使用这些累计值
6. **持久保存**: 数据保存在 resume data 中，跨会话保持

整个流程完全自动化，qBittorrent 应用层无需手动更新这些统计数据。
