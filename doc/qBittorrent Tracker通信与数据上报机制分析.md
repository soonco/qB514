# qBittorrent Tracker 通信与数据上报机制分析

## 核心架构概述

qBittorrent 通过 **libtorrent** 库处理所有与 tracker 的通信，包括数据上报（uploaded/downloaded）。整个流程分为三层：

### 1. **qBittorrent 应用层** (`src/base/bittorrent/`)

* **SessionImpl** - 会话管理器，处理所有 torrent 和 tracker 事件

* **TorrentImpl** - 单个 torrent 的实现，封装 libtorrent 的 torrent\_handle

### 2. **libtorrent 库层** (`deps/libtorrent/1220/`)

* **torrent** - 核心 torrent 逻辑

* **tracker\_manager** - tracker 连接管理

* **http\_tracker\_connection** - HTTP tracker 通信实现

* **udp\_tracker\_connection** - UDP tracker 通信实现

### 3. **数据流向**

## 详细实现分析

### 一、数据统计（上传/下载量）

#### 1. **数据来源** - libtorrent 维护

位置：`deps/libtorrent/1220/include/libtorrent/torrent_status.hpp:281-282`

```cpp
std::int64_t all_time_upload = 0;      // 累计上传量（持久化）
std::int64_t all_time_download = 0;    // 累计下载量（持久化）
std::int64_t total_download = 0;       // 本次会话下载量
std::int64_t total_upload = 0;         // 本次会话上传量
```

* `all_time_*` 会保存到 resume data 中，跨会话持久化

* `total_*` 仅记录当前会话，暂停后重置

#### 2. **qBittorrent 获取数据**

位置：`src/base/bittorrent/torrentimpl.cpp:1319-1327`

```cpp
qlonglong TorrentImpl::totalDownload() const
{
    return m_nativeStatus.all_time_download;  // 从 libtorrent 获取
}

qlonglong TorrentImpl::totalUpload() const
{
    return m_nativeStatus.all_time_upload;    // 从 libtorrent 获取
}
```

`m_nativeStatus` 是 libtorrent 的 `torrent_status` 对象的缓存。

### 二、Tracker 通告（Announce）流程

#### 1. **触发 Announce**

位置：`src/base/bittorrent/torrentimpl.cpp:1638-1641`

```cpp
void TorrentImpl::forceReannounce(const int index)
{
    m_nativeHandle.force_reannounce(0, index);  // 调用 libtorrent API
}
```

也可由 SessionImpl 触发：
`src/base/bittorrent/sessionimpl.cpp:4952`

#### 2. **libtorrent 构建 Announce 请求**

位置：`deps/libtorrent/1220/src/http_tracker_connection.cpp:122-145`

关键代码：

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

**关键点**：

* `tracker_req().uploaded` 和 `tracker_req().downloaded` 来自 `torrent_status` 的 `all_time_upload` 和 `all_time_download`

* 这些值会在每次 announce 时自动发送给 tracker

#### 3. **处理 Tracker 响应**

位置：`src/base/bittorrent/sessionimpl.cpp:5816-5820, 6408-6418`

```cpp
// 监听 tracker 警报
case lt::tracker_announce_alert::alert_type:
case lt::tracker_error_alert::alert_type:
case lt::tracker_reply_alert::alert_type:
case lt::tracker_warning_alert::alert_type:
    handleTrackerAlert(static_cast<const lt::tracker_alert *>(alert));
    break;
```

处理 tracker 回复：

```cpp
if (alert->type() == lt::tracker_reply_alert::alert_type)
{
    const int numPeers = static_cast<const lt::tracker_reply_alert *>(alert)->num_peers;
    // 更新 tracker 状态
}
```

### 三、完整调用链

```
用户操作/定时器
    ↓
qBittorrent::TorrentImpl::forceReannounce()
    ↓
libtorrent::torrent_handle::force_reannounce()
    ↓
libtorrent::torrent (内部逻辑)
    ↓
libtorrent::tracker_manager (管理 tracker 连接)
    ↓
libtorrent::http_tracker_connection::start()
    ↓
构建 HTTP GET 请求（包含 uploaded/downloaded）
    ↓
发送到 Tracker 服务器
    ↓
接收响应（peer 列表、间隔时间等）
    ↓
libtorrent 发出 tracker_reply_alert
    ↓
qBittorrent::SessionImpl::handleTrackerAlert()
    ↓
更新 UI/状态
```

### 四、关键文件清单

#### qBittorrent 层：

1. **src/base/bittorrent/sessionimpl.cpp** - 会话管理，处理 tracker 警报
2. **src/base/bittorrent/torrentimpl.cpp** - torrent 实现，获取上传下载数据
3. **src/base/bittorrent/tracker.cpp** - 内嵌 tracker 服务器（可选功能）

#### libtorrent 层：

1. **deps/libtorrent/1220/src/http\_tracker\_connection.cpp** - HTTP tracker 通信
2. **deps/libtorrent/1220/src/tracker\_manager.cpp** - tracker 管理器
3. **deps/libtorrent/1220/src/torrent.cpp** - torrent 核心逻辑
4. **deps/libtorrent/1220/include/libtorrent/torrent\_status.hpp** - 状态结构定义

### 五、数据持久化

* libtorrent 会将 `all_time_upload` 和 `all_time_download` 保存到 **resume data**

* qBittorrent 在 `SessionImpl` 中也维护会话级别的统计：

  ```cpp
  m_status.allTimeDownload = m_previouslyDownloaded + m_status.totalDownload;
  m_status.allTimeUpload = m_previouslyUploaded + m_status.totalUpload;
  ```

### 六、总结

**核心机制**：

1. **libtorrent 自动维护** 上传下载统计（`torrent_status::all_time_*`）
2. **每次 announce 时自动上报** 这些数据到 tracker
3. **qBittorrent 仅需调用** `force_reannounce()` 触发通告
4. **所有底层细节** 由 libtorrent 处理，包括：

   * 构建请求 URL

   * 添加必需参数

   * 处理响应

   * 发出警报通知

这种设计使得 qBittorrent 无需关心 tracker 协议细节，只需通过 libtorrent 的高层 API 即可完成所有 tracker 交互。
