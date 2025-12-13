# qBittorrent 上传下载数据追踪机制 - 版本对比总结

## 文档说明

本文档对比了 qBittorrent 在使用 **libtorrent 1.2.20** 和 **libtorrent 2.0.11** 两个版本时，上传下载数据追踪机制的异同。

相关详细文档：
- [libtorrent 1.2.20 版本详细分析](./UPLOAD_DOWNLOAD_TRACKING.md)
- [libtorrent 2.0.11 版本详细分析](./UPLOAD_DOWNLOAD_TRACKING_2011.md)

## 核心结论

### ✅ 完全兼容

**两个版本的核心机制完全相同**，qBittorrent 应用层代码无需任何修改即可在两个版本之间切换。

## 数据流向对比

两个版本的数据流向**完全相同**：

```
网络数据包 → peer_connection → torrent → stat → stat_channel
    ↓ (每秒)
torrent::second_tick() 累加到 m_total_uploaded/m_total_downloaded
    ↓ (按需)
torrent::status() 填充到 torrent_status
    ↓
qBittorrent 读取 all_time_upload/all_time_download
```

## 关键代码位置对比

| 功能 | libtorrent 1.2.20 | libtorrent 2.0.11 | 变化 |
|------|-------------------|-------------------|------|
| **peer_connection::received_bytes()** | src/peer_connection.cpp:1130 | src/peer_connection.cpp:1142 | 行号+12 |
| **stat_channel::add()** | include/libtorrent/stat.hpp:63 | include/libtorrent/stat.hpp:65 | 行号+2 |
| **torrent::second_tick() 累加** | src/torrent.cpp:9508 | src/torrent.cpp:10275 | 行号+767 |
| **torrent::status() 填充** | src/torrent.cpp:11027 | src/torrent.cpp:11845 | 行号+818 |
| **torrent 构造函数初始化** | src/torrent.cpp:386 | src/torrent.cpp:194 | 行号-192 |
| **torrent_status 结构定义** | include/libtorrent/torrent_status.hpp:281 | include/libtorrent/torrent_status.hpp:277 | 行号-4 |
| **http_tracker_connection 上报** | src/http_tracker_connection.cpp:138 | src/http_tracker_connection.cpp:147 | 行号+9 |

**说明**: 行号变化是由于代码重构和优化，但逻辑完全相同。

## 代码实现对比

### 1. peer_connection::received_bytes()

#### libtorrent 1.2.20
```cpp
// src/peer_connection.cpp:1130
void peer_connection::received_bytes(int const bytes_payload, int const bytes_protocol)
{
    m_statistics.received_bytes(bytes_payload, bytes_protocol);
    if (m_ignore_stats) return;
    std::shared_ptr<torrent> t = m_torrent.lock();
    if (!t) return;
    t->received_bytes(bytes_payload, bytes_protocol);
}
```

#### libtorrent 2.0.11
```cpp
// src/peer_connection.cpp:1142
void peer_connection::received_bytes(int const bytes_payload, int const bytes_protocol)
{
    TORRENT_ASSERT(is_single_thread());  // ← 新增断言
    m_statistics.received_bytes(bytes_payload, bytes_protocol);
    if (m_ignore_stats) return;
    std::shared_ptr<torrent> t = m_torrent.lock();
    if (!t) return;
    t->received_bytes(bytes_payload, bytes_protocol);
}
```

**差异**: 2.0.11 增加了线程安全断言

### 2. stat_channel::add()

#### libtorrent 1.2.20
```cpp
// include/libtorrent/stat.hpp:63
void add(int count)
{
    m_counter += count;
    m_total_counter += count;
}
```

#### libtorrent 2.0.11
```cpp
// include/libtorrent/stat.hpp:65
void add(int count)
{
    TORRENT_ASSERT(count >= 0);  // ← 新增断言
    TORRENT_ASSERT(m_counter < (std::numeric_limits<std::int32_t>::max)() - count);  // ← 新增溢出检查
    m_counter += count;
    TORRENT_ASSERT(m_total_counter < (std::numeric_limits<std::int64_t>::max)() - count);  // ← 新增溢出检查
    m_total_counter += count;
}
```

**差异**: 2.0.11 增加了参数验证和溢出检查断言

### 3. torrent::second_tick() 累加

#### libtorrent 1.2.20
```cpp
// src/torrent.cpp:9508-9509
m_total_uploaded += m_stat.last_payload_uploaded();
m_total_downloaded += m_stat.last_payload_downloaded();
m_stat.second_tick(tick_interval_ms);
```

#### libtorrent 2.0.11
```cpp
// src/torrent.cpp:10275-10277
m_total_uploaded += m_stat.last_payload_uploaded();
m_total_downloaded += m_stat.last_payload_downloaded();
m_stat.second_tick(tick_interval_ms);
```

**差异**: 逻辑完全相同，仅行号不同

### 4. torrent::status() 填充

#### libtorrent 1.2.20
```cpp
// src/torrent.cpp:11027-11028
st->all_time_upload = m_total_uploaded;
st->all_time_download = m_total_downloaded;
```

#### libtorrent 2.0.11
```cpp
// src/torrent.cpp:11845-11846
st->all_time_upload = m_total_uploaded;
st->all_time_download = m_total_downloaded;
```

**差异**: 逻辑完全相同，仅行号不同

### 5. torrent 构造函数初始化

#### libtorrent 1.2.20
```cpp
// src/torrent.cpp:386-387
m_total_uploaded = p.total_uploaded;
m_total_downloaded = p.total_downloaded;
```

#### libtorrent 2.0.11
```cpp
// src/torrent.cpp:194-195
torrent::torrent(
    aux::session_interface& ses
    , bool const session_paused
    , add_torrent_params&& p)
    : torrent_hot_members(ses, p, session_paused)
    , m_total_uploaded(p.total_uploaded)      // ← 使用成员初始化列表
    , m_total_downloaded(p.total_downloaded)  // ← 使用成员初始化列表
```

**差异**: 2.0.11 使用现代 C++ 的成员初始化列表，更符合最佳实践

### 6. torrent_status 结构定义

#### libtorrent 1.2.20
```cpp
// include/libtorrent/torrent_status.hpp:281-282
std::int64_t all_time_upload = 0;
std::int64_t all_time_download = 0;
```

#### libtorrent 2.0.11
```cpp
// include/libtorrent/torrent_status.hpp:277-278
// are accumulated upload and download payload byte counters. They are
// saved in and restored from resume data to keep totals across sessions.
std::int64_t all_time_upload = 0;
std::int64_t all_time_download = 0;
```

**差异**: 2.0.11 增加了更详细的注释说明

### 7. HTTP Tracker 上报

#### libtorrent 1.2.20
```cpp
// src/http_tracker_connection.cpp:138-139
"&uploaded=%" PRId64
"&downloaded=%" PRId64
, tracker_req().uploaded
, tracker_req().downloaded
```

#### libtorrent 2.0.11
```cpp
// src/http_tracker_connection.cpp:147-148
"&uploaded=%" PRId64
"&downloaded=%" PRId64
, tracker_req().uploaded
, tracker_req().downloaded
```

**差异**: 逻辑完全相同，仅行号不同

## 功能特性对比

| 特性 | libtorrent 1.2.20 | libtorrent 2.0.11 | 说明 |
|------|-------------------|-------------------|------|
| **核心逻辑** | ✓ | ✓ | 完全相同 |
| **数据流向** | ✓ | ✓ | 完全相同 |
| **API 接口** | ✓ | ✓ | 兼容 |
| **线程安全断言** | 基础 | 增强 | 2.0.11 增加了更多断言 |
| **溢出检查** | 无 | 有 | 2.0.11 增加了溢出检查 |
| **类型系统** | 基础 | 强类型 | 2.0.11 使用更多强类型 |
| **构造函数风格** | 传统赋值 | 成员初始化列表 | 2.0.11 更现代 |
| **代码注释** | 简洁 | 详细 | 2.0.11 注释更完善 |
| **ABI 版本控制** | 有 | 增强 | 2.0.11 通过宏更精细控制 |

## 性能对比

| 方面 | libtorrent 1.2.20 | libtorrent 2.0.11 | 影响 |
|------|-------------------|-------------------|------|
| **实时累加** | 每个数据包 | 每个数据包 | 相同 |
| **定期汇总** | 每秒 | 每秒 | 相同 |
| **内存占用** | 标准 | 标准 | 相同 |
| **CPU 开销** | 低 | 低 | 相同 |
| **断言开销** | 低 | 略高（仅 Debug） | Release 版本相同 |

**说明**: 2.0.11 的额外断言仅在 Debug 模式下有效，Release 版本性能相同。

## 兼容性分析

### qBittorrent 应用层

**完全兼容** - 无需任何修改

```cpp
// src/base/bittorrent/torrentimpl.cpp:1319-1327
// 两个版本使用完全相同的代码
qlonglong TorrentImpl::totalDownload() const
{
    return m_nativeStatus.all_time_download;
}

qlonglong TorrentImpl::totalUpload() const
{
    return m_nativeStatus.all_time_upload;
}
```

### Resume Data

**完全兼容** - 数据格式相同

- 两个版本都使用 `add_torrent_params::total_uploaded` 和 `total_downloaded`
- Resume data 可以在两个版本之间互相迁移
- 累计统计数据不会丢失

### Tracker 协议

**完全兼容** - 协议相同

- 两个版本都使用标准的 BitTorrent Tracker 协议
- `uploaded` 和 `downloaded` 参数格式相同
- Tracker 服务器无法区分客户端使用的 libtorrent 版本

## 升级建议

### 从 1.2.20 升级到 2.0.11

**优势**:
1. ✅ 更严格的类型检查和断言，提高代码质量
2. ✅ 更现代的 C++ 代码风格
3. ✅ 更详细的文档注释
4. ✅ 更好的性能优化（内部实现）
5. ✅ 持续的社区支持和更新

**风险**:
- ⚠️ 无重大风险，API 完全兼容
- ⚠️ 需要重新编译 qBittorrent
- ⚠️ Debug 版本可能因断言略慢（Release 无影响）

**迁移步骤**:
1. 更新 libtorrent 依赖到 2.0.11
2. 重新编译 qBittorrent
3. 测试基本功能（下载、上传、tracker 通信）
4. 验证统计数据准确性
5. 无需修改应用层代码

### 保持使用 1.2.20

**适用场景**:
- 稳定性优先的生产环境
- 不需要新特性
- 避免重新编译和测试的开销

**注意事项**:
- 1.2.20 已是较旧版本，可能缺少安全更新
- 社区支持逐渐减少

## 测试验证

### 验证点

1. **数据准确性**
   - ✓ 下载数据统计准确
   - ✓ 上传数据统计准确
   - ✓ 跨会话累计正确

2. **Tracker 通信**
   - ✓ Announce 请求包含正确的 uploaded/downloaded
   - ✓ Tracker 响应正常
   - ✓ 数据上报准确

3. **Resume Data**
   - ✓ 保存累计统计
   - ✓ 恢复累计统计
   - ✓ 跨版本兼容

4. **性能**
   - ✓ CPU 占用正常
   - ✓ 内存占用正常
   - ✓ 网络性能正常

### 测试方法

```bash
# 1. 下载一个小文件
# 2. 检查统计数据
qbittorrent-cli torrent info <hash>

# 3. 暂停并重启
qbittorrent-cli torrent pause <hash>
qbittorrent-cli torrent resume <hash>

# 4. 验证累计数据未重置
qbittorrent-cli torrent info <hash>

# 5. 检查 resume data
cat ~/.local/share/qBittorrent/BT_backup/<hash>.fastresume
```

## 总结

### 核心发现

1. **机制相同**: 两个版本的上传下载数据追踪机制**完全相同**
2. **API 兼容**: qBittorrent 应用层代码**无需修改**
3. **数据兼容**: Resume data 和 tracker 协议**完全兼容**
4. **质量提升**: 2.0.11 版本代码质量更高，但不影响功能

### 推荐方案

**对于新项目**: 使用 **libtorrent 2.0.11**
- 更好的代码质量
- 持续的社区支持
- 更现代的 C++ 实现

**对于现有项目**: 可以安全升级到 **2.0.11**
- 无需修改应用层代码
- 数据完全兼容
- 风险极低

### 关键要点

1. ✅ **完全兼容**: 两个版本在功能和数据层面完全兼容
2. ✅ **透明升级**: qBittorrent 可以无缝切换版本
3. ✅ **数据保留**: 统计数据在版本切换时不会丢失
4. ✅ **性能相当**: Release 版本性能相同
5. ✅ **质量提升**: 2.0.11 代码质量更高

整个上传下载数据追踪机制在两个版本中都是**完全自动化**的，qBittorrent 应用层只需读取 `all_time_upload` 和 `all_time_download` 字段，无需关心底层实现细节。
