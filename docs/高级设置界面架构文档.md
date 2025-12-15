# qBittorrent Advanced Settings 界面架构文档

## 概述

Advanced Settings（高级设置）是 qBittorrent 中用于配置高级参数的界面组件，位于 `src/gui/advancedsettings.cpp`。该界面采用程序化 UI 构建方式，使用 `QTableWidget` 作为基础容器，通过枚举驱动的布局机制实现灵活的设置项管理。

## 文件位置

- **源文件**: `/src/gui/advancedsettings.cpp`
- **头文件**: `/src/gui/advancedsettings.h`
- **配置持久化**: `~/.config/qBittorrent/qBittorrent.ini` (macOS/Linux)

## 核心架构

### 1. 类继承关系

```cpp
class AdvancedSettings : public GUIApplicationComponent<QTableWidget>
```

- 继承自 `QTableWidget`，直接作为表格控件使用
- 无独立的 `.ui` 文件，所有 UI 元素通过代码动态创建

### 2. 表格结构

#### 列定义 (AdvSettingsCols)

```cpp
enum AdvSettingsCols
{
    PROPERTY,  // 第 0 列：设置项名称
    VALUE,     // 第 1 列：设置项的值（控件）
    COL_COUNT  // 列总数：2
};
```

#### 行定义 (AdvSettingsRows)

通过枚举定义所有设置项的行号，枚举顺序直接决定界面显示顺序：

```cpp
enum AdvSettingsRows
{
    // qBittorrent Section
    QBITTORRENT_HEADER,              // 分组标题
    RESUME_DATA_STORAGE,
    TORRENT_CONTENT_REMOVE_OPTION,
    MEMORY_WORKING_SET_LIMIT,        // 条件编译
    OS_MEMORY_PRIORITY,              // 条件编译
    NETWORK_IFACE,
    NETWORK_IFACE_ADDRESS,
    SAVE_RESUME_DATA_INTERVAL,
    SAVE_STATISTICS_INTERVAL,
    TORRENT_FILE_SIZE_LIMIT,
    CONFIRM_RECHECK_TORRENT,
    RECHECK_COMPLETED,
    APP_INSTANCE_NAME,               // 应用实例名称
    LIST_REFRESH,
    RESOLVE_HOSTS,
    RESOLVE_COUNTRIES,
    PROGRAM_NOTIFICATIONS,
    TORRENT_ADDED_NOTIFICATIONS,
    NOTIFICATION_TIMEOUT,            // 条件编译
    CONFIRM_REMOVE_ALL_TAGS,
    CONFIRM_REMOVE_TRACKER_FROM_ALL_TORRENTS,
    REANNOUNCE_WHEN_ADDRESS_CHANGED,
    DOWNLOAD_TRACKER_FAVICON,
    SAVE_PATH_HISTORY_LENGTH,
    ENABLE_SPEED_WIDGET,
    ENABLE_ICONS_IN_MENUS,           // 条件编译
    USE_ATTACHED_ADD_NEW_TORRENT_DIALOG, // 条件编译
    TRACKER_STATUS,
    TRACKER_PORT,
    TRACKER_PORT_FORWARDING,
    ENABLE_MARK_OF_THE_WEB,          // 条件编译
    IGNORE_SSL_ERRORS,
    PYTHON_EXECUTABLE_PATH,
    START_SESSION_PAUSED,
    SESSION_SHUTDOWN_TIMEOUT,

    // libtorrent Section
    LIBTORRENT_HEADER,               // 分组标题
    BDECODE_DEPTH_LIMIT,
    BDECODE_TOKEN_LIMIT,
    ASYNC_IO_THREADS,
    HASHING_THREADS,                 // 条件编译
    FILE_POOL_SIZE,
    CHECKING_MEM_USAGE,
    DISK_CACHE,                      // 条件编译
    DISK_CACHE_TTL,                  // 条件编译
    DISK_QUEUE_SIZE,
    DISK_IO_TYPE,                    // 条件编译
    DISK_IO_READ_MODE,
    DISK_IO_WRITE_MODE,
    COALESCE_RW,                     // 条件编译
    PIECE_EXTENT_AFFINITY,
    SUGGEST_MODE,
    SEND_BUF_WATERMARK,
    SEND_BUF_LOW_WATERMARK,
    SEND_BUF_WATERMARK_FACTOR,
    CONNECTION_SPEED,
    SOCKET_SEND_BUFFER_SIZE,
    SOCKET_RECEIVE_BUFFER_SIZE,
    SOCKET_BACKLOG_SIZE,
    OUTGOING_PORT_MIN,
    OUTGOING_PORT_MAX,
    UPNP_LEASE_DURATION,
    PEER_TOS,
    UTP_MIX_MODE,
    IDN_SUPPORT,
    MULTI_CONNECTIONS_PER_IP,
    VALIDATE_HTTPS_TRACKER_CERTIFICATE,
    SSRF_MITIGATION,
    BLOCK_PEERS_ON_PRIVILEGED_PORTS,
    CHOKING_ALGORITHM,
    SEED_CHOKING_ALGORITHM,
    ANNOUNCE_ALL_TRACKERS,
    ANNOUNCE_ALL_TIERS,
    ANNOUNCE_IP,
    ANNOUNCE_PORT,
    MAX_CONCURRENT_HTTP_ANNOUNCES,
    STOP_TRACKER_TIMEOUT,
    PEER_TURNOVER,
    PEER_TURNOVER_CUTOFF,
    PEER_TURNOVER_INTERVAL,
    REQUEST_QUEUE_SIZE,
    DHT_BOOTSTRAP_NODES,
    I2P_INBOUND_QUANTITY,            // 条件编译
    I2P_OUTBOUND_QUANTITY,           // 条件编译
    I2P_INBOUND_LENGTH,              // 条件编译
    I2P_OUTBOUND_LENGTH,             // 条件编译

    ROW_COUNT  // 总行数
};
```

### 3. 核心方法

#### 构造函数

```cpp
AdvancedSettings::AdvancedSettings(IGUIApplication *app, QWidget *parent)
    : GUIApplicationComponent(app, parent)
{
    setColumnCount(COL_COUNT);
    setHorizontalHeaderLabels({tr("Setting"), tr("Value")});
    setRowCount(ROW_COUNT);
    verticalHeader()->setVisible(false);
    setAlternatingRowColors(true);
    setSelectionMode(QAbstractItemView::NoSelection);
    setEditTriggers(QAbstractItemView::NoEditTriggers);
    
    loadAdvancedSettings();
    resizeColumnToContents(0);
    horizontalHeader()->setStretchLastSection(true);
}
```

#### addRow 模板方法

这是布局的核心方法，负责将设置项添加到表格中：

```cpp
template <typename T>
void AdvancedSettings::addRow(const int row, const QString &text, T *widget)
{
    // 创建左侧标签
    auto *label = new QLabel(text);
    label->setOpenExternalLinks(true);
    label->setToolTip(widget->toolTip());

    // 将标签放在 PROPERTY 列（第 0 列）
    setCellWidget(row, PROPERTY, label);
    
    // 将控件放在 VALUE 列（第 1 列）
    setCellWidget(row, VALUE, widget);

    // 根据控件类型连接信号
    if constexpr (std::is_same_v<T, QCheckBox>)
        connect(widget, &QCheckBox::stateChanged, this, &AdvancedSettings::settingsChanged);
    else if constexpr (std::is_same_v<T, QSpinBox>)
        connect(widget, &QSpinBox::valueChanged, this, &AdvancedSettings::settingsChanged);
    else if constexpr (std::is_same_v<T, QComboBox>)
        connect(widget, &QComboBox::currentIndexChanged, this, &AdvancedSettings::settingsChanged);
    else if constexpr (std::is_same_v<T, QLineEdit>)
        connect(widget, &QLineEdit::textChanged, this, &AdvancedSettings::settingsChanged);
}
```

#### loadAdvancedSettings

从配置系统加载所有设置值并初始化控件：

```cpp
void AdvancedSettings::loadAdvancedSettings()
{
    const Preferences *const pref = Preferences::instance();
    const BitTorrent::Session *const session = BitTorrent::Session::instance();

    // 添加分组标题
    addSectionHeaders();
    
    // 逐个添加设置项
    // 示例：
    m_lineEditAppInstanceName.setText(app()->instanceName());
    m_lineEditAppInstanceName.setToolTip(tr("It appends the text to the window title..."));
    addRow(APP_INSTANCE_NAME, tr("Customize application instance name"), &m_lineEditAppInstanceName);
}
```

#### saveAdvancedSettings

将所有设置保存到配置系统：

```cpp
void AdvancedSettings::saveAdvancedSettings() const
{
    Preferences *const pref = Preferences::instance();
    BitTorrent::Session *const session = BitTorrent::Session::instance();

    // 示例：
    app()->setInstanceName(m_lineEditAppInstanceName.text());
    pref->setBdecodeDepthLimit(m_spinBoxBdecodeDepthLimit.value());
    session->setAsyncIOThreads(m_spinBoxAsyncIOThreads.value());
    // ... 保存所有设置
}
```

## 布局机制详解

### 枚举驱动的布局系统

这是 Advanced Settings 最核心的设计特点：

1. **枚举定义顺序 = 界面显示顺序**
   - 在 `AdvSettingsRows` 枚举中的位置直接决定在表格中的行号
   - 无需手动计算行号，枚举值自动递增

2. **分组通过标题行实现**
   - `QBITTORRENT_HEADER` 和 `LIBTORRENT_HEADER` 是特殊的标题行
   - 标题行使用粗体文本和居中对齐

3. **条件编译支持**
   - 使用 `#ifdef` 控制特定平台或配置下的设置项
   - 枚举中被排除的项不会占用行号

### 添加新设置项的步骤

假设要在 qBittorrent Section 中添加一个新的 CheckBox 设置：

#### 步骤 1: 在枚举中添加行标识

```cpp
enum AdvSettingsRows
{
    QBITTORRENT_HEADER,
    // ... 其他设置项
    APP_INSTANCE_NAME,
    MY_NEW_SETTING,        // 新增：在期望的位置添加
    LIST_REFRESH,
    // ...
};
```

#### 步骤 2: 在头文件中声明控件成员

```cpp
// advancedsettings.h
class AdvancedSettings : public GUIApplicationComponent<QTableWidget>
{
    // ...
private:
    QCheckBox m_checkBoxMyNewSetting;  // 新增控件
    // ... 其他控件
};
```

#### 步骤 3: 在 loadAdvancedSettings 中初始化

```cpp
void AdvancedSettings::loadAdvancedSettings()
{
    // ...
    
    // 新增：加载设置值
    m_checkBoxMyNewSetting.setChecked(pref->getMyNewSetting());
    addRow(MY_NEW_SETTING, tr("My new setting description"), &m_checkBoxMyNewSetting);
    
    // ...
}
```

#### 步骤 4: 在 saveAdvancedSettings 中保存

```cpp
void AdvancedSettings::saveAdvancedSettings() const
{
    // ...
    
    // 新增：保存设置值
    pref->setMyNewSetting(m_checkBoxMyNewSetting.isChecked());
    
    // ...
}
```

## 界面布局效果

```
┌────────────────────────────────────────────────────────────────────┐
│ Setting                                    │ Value                 │
├────────────────────────────────────────────────────────────────────┤
│          **qBittorrent Section**           │ Open documentation    │
├────────────────────────────────────────────────────────────────────┤
│ Resume data storage type                   │ [ComboBox ▼]         │
│ Torrent content removing mode              │ [ComboBox ▼]         │
│ Physical memory usage limit                │ [1024    ] MiB       │
│ Network interface                          │ [ComboBox ▼]         │
│ Optional IP address to bind to             │ [ComboBox ▼]         │
│ Save resume data interval                  │ [60      ] min       │
│ Save statistics interval                   │ [15      ] min       │
│ Torrent file size limit                    │ [100     ] MiB       │
│ Confirm torrent recheck                    │ [☑]                  │
│ Recheck torrents on completion             │ [☐]                  │
│ Customize application instance name        │ [____________]       │
│ Refresh interval                           │ [1500    ] ms        │
│ Resolve peer countries                     │ [☑]                  │
│ Resolve peer host names                    │ [☐]                  │
│ Program notifications                      │ [☑]                  │
│ Torrent added notifications                │ [☐]                  │
│ Confirm removal of all tags                │ [☑]                  │
│ Confirm removal of tracker from all...     │ [☑]                  │
│ Reannounce when address changed            │ [☐]                  │
│ Download tracker favicon                   │ [☑]                  │
│ Save path history length                   │ [8       ]           │
│ Enable speed widget                        │ [☑]                  │
│ Enable icons in menus                      │ [☑]                  │
│ Enable embedded tracker                    │ [☐]                  │
│ Embedded tracker port                      │ [9000    ]           │
│ Enable port forwarding for embedded...     │ [☐]                  │
│ Ignore SSL errors                          │ [☐]                  │
│ Python executable path                     │ [____________]       │
│ Start session paused                       │ [☐]                  │
│ Session shutdown timeout                   │ [60      ] s         │
├────────────────────────────────────────────────────────────────────┤
│          **libtorrent Section**            │ Open documentation    │
├────────────────────────────────────────────────────────────────────┤
│ Bdecode depth limit                        │ [100     ]           │
│ Bdecode token limit                        │ [3000000 ]           │
│ Asynchronous I/O threads                   │ [10      ]           │
│ Hashing threads                            │ [2       ]           │
│ File pool size                             │ [5000    ]           │
│ Outstanding memory when checking...        │ [32      ] MiB       │
│ Disk queue size                            │ [1024    ] KiB       │
│ Disk IO type                               │ [ComboBox ▼]         │
│ Disk IO read mode                          │ [ComboBox ▼]         │
│ Disk IO write mode                         │ [ComboBox ▼]         │
│ Use piece extent affinity                  │ [☐]                  │
│ Send upload piece suggestions              │ [☐]                  │
│ Send buffer watermark                      │ [500     ] KiB       │
│ Send buffer low watermark                  │ [10      ] KiB       │
│ Send buffer watermark factor               │ [50      ] %         │
│ Outgoing connections per second            │ [20      ]           │
│ Socket send buffer size                    │ [0       ] KiB       │
│ Socket receive buffer size                 │ [0       ] KiB       │
│ Socket backlog size                        │ [30      ]           │
│ Outgoing ports (Min) [0: disabled]         │ [0       ]           │
│ Outgoing ports (Max) [0: disabled]         │ [0       ]           │
│ UPnP lease duration [0: permanent]         │ [0       ] s         │
│ Peer ToS                                   │ [0       ]           │
│ μTP-TCP mixed mode                         │ [ComboBox ▼]         │
│ Support internationalized domain name      │ [☑]                  │
│ Allow multiple connections from same IP    │ [☐]                  │
│ Validate HTTPS tracker certificates        │ [☑]                  │
│ Server-side request forgery mitigation     │ [☑]                  │
│ Disallow connection to peers on...         │ [☑]                  │
│ Choking algorithm                          │ [ComboBox ▼]         │
│ Seed choking algorithm                     │ [ComboBox ▼]         │
│ Always announce to all trackers            │ [☐]                  │
│ Always announce to all tiers               │ [☑]                  │
│ IP address reported to trackers            │ [____________]       │
│ Port reported to trackers                  │ [0       ]           │
│ Max concurrent HTTP announces              │ [50      ]           │
│ Stop tracker timeout                       │ [5       ] s         │
│ Peer turnover disconnect percentage        │ [4       ] %         │
│ Peer turnover threshold percentage         │ [90      ] %         │
│ Peer turnover disconnect interval          │ [300     ] s         │
│ Maximum outstanding requests to peer       │ [500     ]           │
│ DHT bootstrap nodes                        │ [____________]       │
└────────────────────────────────────────────────────────────────────┘
```

## 配置持久化机制

### 存储架构

```
AdvancedSettings
    ↓ (调用)
Preferences / BitTorrent::Session
    ↓ (调用)
SettingsStorage
    ↓ (使用)
QSettings
    ↓ (写入)
qBittorrent.ini
```

### 配置文件位置

| 平台 | 路径 |
|------|------|
| macOS | `~/.config/qBittorrent/qBittorrent.ini` |
| Linux | `~/.config/qBittorrent/qBittorrent.conf` |
| Windows | `%APPDATA%\qBittorrent\qBittorrent.ini` |

### 安全写入机制

1. 先写入临时文件 `qBittorrent_new.ini`
2. 写入成功后替换原文件
3. 防止断电或磁盘满导致配置丢失
4. 自动延迟保存（5秒后批量写入）

### 配置文件格式示例

```ini
[Application]
InstanceName=MyInstance

[BitTorrent]
Session\AsyncIOThreads=10
Session\HashingThreads=2
Session\FilePoolSize=5000
Session\CheckingMemUsage=32

[Preferences]
Advanced\BdecodeDepthLimit=100
Advanced\BdecodeTokenLimit=3000000
```

## 控件类型说明

| 控件类型 | 用途 | 示例 |
|---------|------|------|
| QSpinBox | 数值输入 | 端口号、线程数、时间间隔 |
| QCheckBox | 布尔选项 | 启用/禁用功能 |
| QComboBox | 下拉选择 | 模式选择、算法选择 |
| QLineEdit | 文本输入 | IP 地址、路径、实例名称 |
| QLabel | 分组标题 | qBittorrent Section、libtorrent Section |

## 国际化支持

所有用户可见的文本都使用 `tr()` 函数包裹：

```cpp
addRow(APP_INSTANCE_NAME, 
       tr("Customize application instance name"),  // 可翻译
       &m_lineEditAppInstanceName);

m_lineEditAppInstanceName.setToolTip(
    tr("It appends the text to the window title to help distinguish qBittorent instances")
);
```

## 文档链接

界面中包含两类文档链接：

1. **分组标题链接**: 指向 qBittorrent Wiki
   - qBittorrent Section: `https://github.com/qbittorrent/qBittorrent/wiki/Explanation-of-Options-in-qBittorrent#Advanced`
   - libtorrent Section: `https://www.libtorrent.org/reference-Settings.html`

2. **设置项帮助链接**: 每个设置项后的 `(?)` 链接
   - 指向 libtorrent 官方文档的具体参数说明
   - 示例: `https://www.libtorrent.org/reference-Settings.html#aio_threads`

## 条件编译

根据不同平台和编译选项，部分设置项会动态显示或隐藏：

| 宏定义 | 影响的设置项 |
|--------|-------------|
| `QBT_USES_LIBTORRENT2` | Hashing threads, Disk IO type, Memory working set limit |
| `Q_OS_WIN` | OS memory priority, Mark of the web |
| `Q_OS_MACOS` | Mark of the web (排除 Icons in menus) |
| `QBT_USES_DBUS` | Notification timeout |
| `TORRENT_USE_I2P` | I2P 相关设置 |
| `QBT_APP_64BIT` | 影响某些 SpinBox 的最大值 |

## 信号与槽

每个控件的值改变时会发出 `settingsChanged` 信号：

```cpp
signals:
    void settingsChanged();
```

这个信号通常被父对话框（Options Dialog）监听，用于：
- 启用"应用"按钮
- 标记配置已修改
- 触发实时预览（如适用）

## 性能优化

1. **延迟保存**: 配置修改后 5 秒才写入磁盘，避免频繁 I/O
2. **批量更新**: 所有设置一次性保存，而非逐个保存
3. **内存缓存**: `SettingsStorage` 在内存中维护配置副本

## 最佳实践

### 添加新设置项时的注意事项

1. **枚举位置**: 确保添加在正确的分组内
2. **控件初始化**: 设置合理的默认值、最小值、最大值
3. **工具提示**: 为复杂设置提供详细说明
4. **单位后缀**: 使用 `setSuffix()` 明确单位（MiB、KiB、s、ms、%）
5. **特殊值文本**: 对于 0 值等特殊情况，使用 `setSpecialValueText()`
6. **文档链接**: 添加指向官方文档的帮助链接
7. **条件编译**: 考虑跨平台兼容性

### 代码示例：完整的设置项添加

```cpp
// 1. 在枚举中添加
enum AdvSettingsRows
{
    // ...
    MY_NEW_TIMEOUT_SETTING,
    // ...
};

// 2. 在头文件中声明
QSpinBox m_spinBoxMyTimeout;

// 3. 在 loadAdvancedSettings 中初始化
m_spinBoxMyTimeout.setMinimum(0);
m_spinBoxMyTimeout.setMaximum(3600);
m_spinBoxMyTimeout.setValue(pref->getMyTimeout());
m_spinBoxMyTimeout.setSuffix(tr(" s", " seconds"));
m_spinBoxMyTimeout.setSpecialValueText(tr("Disabled"));
m_spinBoxMyTimeout.setToolTip(tr("Set to 0 to disable timeout"));
addRow(MY_NEW_TIMEOUT_SETTING, 
       (tr("My timeout setting") + u' ' + makeLink(u"https://example.com/docs", u"(?)")),
       &m_spinBoxMyTimeout);

// 4. 在 saveAdvancedSettings 中保存
pref->setMyTimeout(m_spinBoxMyTimeout.value());
```

## 相关文件

- `src/gui/advancedsettings.cpp` - 主实现文件
- `src/gui/advancedsettings.h` - 头文件
- `src/base/preferences.cpp` - 配置管理（qBittorrent 设置）
- `src/base/bittorrent/sessionimpl.cpp` - 会话管理（libtorrent 设置）
- `src/base/settingsstorage.cpp` - 底层存储实现
- `src/gui/optionsdialog.cpp` - 父对话框

## 调试技巧

### 查看当前配置值

```bash
# macOS/Linux
cat ~/.config/qBittorrent/qBittorrent.ini | grep -A 5 "\[BitTorrent\]"
```

### 重置配置

```bash
# 备份并删除配置文件
mv ~/.config/qBittorrent/qBittorrent.ini ~/.config/qBittorrent/qBittorrent.ini.backup
```

### 追踪配置保存

在 `saveAdvancedSettings()` 中添加调试输出：

```cpp
qDebug() << "Saving AsyncIOThreads:" << m_spinBoxAsyncIOThreads.value();
```

## 常见问题

### Q: 为什么我的设置项没有显示？

A: 检查以下几点：
1. 枚举是否在条件编译块内被排除
2. `loadAdvancedSettings()` 中是否调用了 `addRow()`
3. 控件是否正确初始化

### Q: 如何调整设置项的显示顺序？

A: 只需在 `AdvSettingsRows` 枚举中调整顺序即可，无需修改其他代码。

### Q: 配置何时保存到磁盘？

A: 
1. 用户点击"应用"或"确定"按钮时立即保存
2. 配置修改后 5 秒自动保存
3. 程序退出时保存

### Q: 如何添加平台特定的设置？

A: 使用条件编译：

```cpp
#ifdef Q_OS_WIN
    MY_WINDOWS_ONLY_SETTING,
#endif
```

## 版本历史

- **v4.x**: 引入 libtorrent2 支持，添加新的磁盘 I/O 选项
- **v3.x**: 重构为基于枚举的布局系统
- **v2.x**: 初始实现

## 参考资源

- [qBittorrent Wiki - Advanced Options](https://github.com/qbittorrent/qBittorrent/wiki/Explanation-of-Options-in-qBittorrent#Advanced)
- [libtorrent Settings Reference](https://www.libtorrent.org/reference-Settings.html)
- [Qt QTableWidget Documentation](https://doc.qt.io/qt-6/qtablewidget.html)
- [Qt QSettings Documentation](https://doc.qt.io/qt-6/qsettings.html)

---

**文档版本**: 1.0  
**最后更新**: 2025-12-13  
**适用版本**: qBittorrent 5.x
