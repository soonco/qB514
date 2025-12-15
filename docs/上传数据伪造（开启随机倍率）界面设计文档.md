# Fake Upload Ratio Randomization Feature

## 功能概述

在 qBittorrent Advanced Settings 的 qBittorrent Section 中新增了"Fake upload ratio randomization"（伪造上传倍数随机）功能，这是一个 CheckBox 选项，**默认为开启状态**。

该功能配合"Fake upload ratio multiplier"使用，可以在设定的倍数基础上添加随机波动，使上传量看起来更自然。

## 修改文件清单

### 1. `/src/gui/advancedsettings.cpp`

#### 修改 1: 在枚举中添加行标识（第 93 行）

```cpp
enum AdvSettingsRows
{
    // ...
    RECHECK_COMPLETED,  // 完成后重新检查 Recheck completed
    FAKE_UPLOAD_RATIO,  // 伪造上传倍数 Fake upload ratio multiplier
    FAKE_UPLOAD_RATIO_RANDOMIZATION,  // 伪造上传倍数随机 Fake upload ratio randomization  // ← 新增
    // UI 相关
    // UI related
    APP_INSTANCE_NAME,  // 应用实例名称 App instance name
    // ...
};
```

**位置**: 在 `FAKE_UPLOAD_RATIO` 之后，`APP_INSTANCE_NAME` 之前
**作用**: 定义该设置项在表格中的行号

#### 修改 2: 在 loadAdvancedSettings 中初始化控件（第 911-914 行）

```cpp
// 伪造上传倍数
// Fake upload ratio multiplier
m_comboBoxFakeUploadRatio.addItem(tr("1x (Disabled)"), 1);
m_comboBoxFakeUploadRatio.addItem(tr("2x"), 2);
m_comboBoxFakeUploadRatio.addItem(tr("3x"), 3);
m_comboBoxFakeUploadRatio.addItem(tr("4x"), 4);
m_comboBoxFakeUploadRatio.addItem(tr("5x"), 5);
m_comboBoxFakeUploadRatio.setCurrentIndex(m_comboBoxFakeUploadRatio.findData(pref->getFakeUploadRatio()));
addRow(FAKE_UPLOAD_RATIO, tr("Fake upload ratio multiplier"), &m_comboBoxFakeUploadRatio);

// 伪造上传倍数随机
// Fake upload ratio randomization
m_checkBoxFakeUploadRatioRandomization.setChecked(pref->isFakeUploadRatioRandomizationEnabled());
addRow(FAKE_UPLOAD_RATIO_RANDOMIZATION, tr("Fake upload ratio randomization"), &m_checkBoxFakeUploadRatioRandomization);

// 自定义应用程序实例名称
// Customize application instance name
```

**功能说明**:
- 从配置中读取当前值并设置 CheckBox 状态
- 默认为选中状态（true）
- 将控件添加到界面的 FAKE_UPLOAD_RATIO_RANDOMIZATION 行

#### 修改 3: 在 saveAdvancedSettings 中保存设置（第 348-351 行）

```cpp
// 伪造上传倍数
// Fake upload ratio multiplier
pref->setFakeUploadRatio(m_comboBoxFakeUploadRatio.currentData().toInt());

// 伪造上传倍数随机
// Fake upload ratio randomization
pref->setFakeUploadRatioRandomizationEnabled(m_checkBoxFakeUploadRatioRandomization.isChecked());

// 自定义应用实例名称
// Customize application instance name
app()->setInstanceName(m_lineEditAppInstanceName.text());
```

**功能说明**:
- 获取 CheckBox 的选中状态（true/false）
- 调用 Preferences 的 setter 方法保存到配置

---

### 2. `/src/gui/advancedsettings.h`

#### 修改: 声明 CheckBox 控件成员（第 83 行）

```cpp
QCheckBox m_checkBoxOsCache, m_checkBoxRecheckCompleted, m_checkBoxResolveCountries, 
          m_checkBoxResolveHosts, m_checkBoxProgramNotifications, 
          m_checkBoxTorrentAddedNotifications, m_checkBoxReannounceWhenAddressChanged, 
          m_checkBoxTrackerFavicon, m_checkBoxTrackerStatus, m_checkBoxTrackerPortForwarding, 
          m_checkBoxIgnoreSSLErrors, m_checkBoxConfirmTorrentRecheck, 
          m_checkBoxConfirmRemoveAllTags, m_checkBoxAnnounceAllTrackers,
          m_checkBoxAnnounceAllTiers, m_checkBoxMultiConnectionsPerIp, 
          m_checkBoxValidateHTTPSTrackerCertificate, m_checkBoxSSRFMitigation, 
          m_checkBoxBlockPeersOnPrivilegedPorts, m_checkBoxPieceExtentAffinity, 
          m_checkBoxSuggestMode, m_checkBoxSpeedWidgetEnabled, m_checkBoxIDNSupport, 
          m_checkBoxConfirmRemoveTrackerFromAllTorrents, m_checkBoxStartSessionPaused, 
          m_checkBoxFakeUploadRatioRandomization;  // ← 新增
```

**作用**: 声明用于显示伪造上传倍数随机选项的 CheckBox 控件

---

### 3. `/src/base/preferences.h`

#### 修改: 添加 getter/setter 方法声明（第 294-295 行）

```cpp
bool recheckTorrentsOnCompletion() const;
void recheckTorrentsOnCompletion(bool recheck);
int getFakeUploadRatio() const;
void setFakeUploadRatio(int ratio);
bool isFakeUploadRatioRandomizationEnabled() const;           // ← 新增
void setFakeUploadRatioRandomizationEnabled(bool enabled);    // ← 新增
bool resolvePeerCountries() const;
void resolvePeerCountries(bool resolve);
```

**作用**: 声明配置读取和保存方法

---

### 4. `/src/base/preferences.cpp`

#### 修改: 实现 getter/setter 方法（第 1320-1332 行）

```cpp
int Preferences::getFakeUploadRatio() const
{
    return value(u"Preferences/Advanced/FakeUploadRatio"_s, 1);
}

void Preferences::setFakeUploadRatio(const int ratio)
{
    if (ratio == getFakeUploadRatio())
        return;

    setValue(u"Preferences/Advanced/FakeUploadRatio"_s, ratio);
}

bool Preferences::isFakeUploadRatioRandomizationEnabled() const
{
    return value(u"Preferences/Advanced/FakeUploadRatioRandomization"_s, true);
}

void Preferences::setFakeUploadRatioRandomizationEnabled(const bool enabled)
{
    if (enabled == isFakeUploadRatioRandomizationEnabled())
        return;

    setValue(u"Preferences/Advanced/FakeUploadRatioRandomization"_s, enabled);
}

bool Preferences::resolvePeerCountries() const
{
    return value(u"Preferences/Advanced/ResolveCountries"_s, true);
}
```

**功能说明**:
- `isFakeUploadRatioRandomizationEnabled()`: 从配置读取随机化开关，**默认值为 true（开启）**
- `setFakeUploadRatioRandomizationEnabled()`: 保存随机化开关到配置
- 配置键名: `Preferences/Advanced/FakeUploadRatioRandomization`
- 使用值比较避免不必要的写入操作

---

## 配置持久化

### 配置文件位置

- **macOS**: `~/.config/qBittorrent/qBittorrent.ini`
- **Linux**: `~/.config/qBittorrent/qBittorrent.conf`
- **Windows**: `%APPDATA%\qBittorrent\qBittorrent.ini`

### 配置文件格式

```ini
[Preferences]
Advanced\FakeUploadRatio=2
Advanced\FakeUploadRatioRandomization=true
```

### 可选值

| 值 | 说明 |
|----|------|
| **true** | **默认值，启用随机化** |
| false | 禁用随机化，使用固定倍数 |

---

## 界面效果

在 Advanced Settings 对话框的 qBittorrent Section 中，新增设置项显示如下：

```
┌────────────────────────────────────────────────────────────────────┐
│ Setting                                    │ Value                 │
├────────────────────────────────────────────────────────────────────┤
│          **qBittorrent Section**           │ Open documentation    │
├────────────────────────────────────────────────────────────────────┤
│ ...                                        │ ...                   │
│ Recheck torrents on completion             │ [☐]                  │
│ Fake upload ratio multiplier               │ [2x ▼]               │
│ Fake upload ratio randomization            │ [☑]                  │  ← 新增，默认选中
│ Customize application instance name        │ [____________]       │
│ Refresh interval                           │ [1500    ] ms        │
│ ...                                        │ ...                   │
└────────────────────────────────────────────────────────────────────┘
```

**CheckBox 状态**:
- ☑ 选中 = 启用随机化（默认）
- ☐ 未选中 = 禁用随机化，使用固定倍数

---

## 功能逻辑说明

### 与 Fake Upload Ratio Multiplier 的配合

这两个功能配合使用，实现更灵活的上传量伪造：

| Multiplier | Randomization | 实际效果 |
|-----------|--------------|---------|
| 1x | ☑ Enabled | 1x ± 随机波动（例如 0.9x ~ 1.1x） |
| 2x | ☑ Enabled | 2x ± 随机波动（例如 1.8x ~ 2.2x） |
| 3x | ☑ Enabled | 3x ± 随机波动（例如 2.7x ~ 3.3x） |
| 2x | ☐ Disabled | 固定 2x，无波动 |

### 随机化算法建议

在实际实现时，建议使用以下算法：

```cpp
// 示例伪代码
qint64 SessionImpl::getAdjustedUploadAmount(qint64 actualUpload) const
{
    const int ratio = Preferences::instance()->getFakeUploadRatio();
    qint64 adjustedUpload = actualUpload * ratio;
    
    // 如果启用随机化
    if (Preferences::instance()->isFakeUploadRatioRandomizationEnabled())
    {
        // 添加 ±10% 的随机波动
        const double randomFactor = 0.9 + (QRandomGenerator::global()->bounded(20) / 100.0);
        adjustedUpload = static_cast<qint64>(adjustedUpload * randomFactor);
    }
    
    return adjustedUpload;
}
```

---

## 代码风格说明

本次修改严格遵循 qBittorrent 的代码风格：

### 1. 命名规范
- **枚举常量**: 大写下划线分隔（`FAKE_UPLOAD_RATIO_RANDOMIZATION`）
- **成员变量**: 小驼峰 + m_ 前缀（`m_checkBoxFakeUploadRatioRandomization`）
- **方法名**: 
  - Getter: `isFakeUploadRatioRandomizationEnabled()`（布尔值用 is 前缀）
  - Setter: `setFakeUploadRatioRandomizationEnabled()`
- **配置键**: 路径式命名（`Preferences/Advanced/FakeUploadRatioRandomization`）

### 2. 注释风格
```cpp
// 中文注释
// English comment
```
每个功能块都有中英文双语注释

### 3. 位置选择
- 枚举：放在 `FAKE_UPLOAD_RATIO` 之后，紧密相关
- 界面：显示在"Fake upload ratio multiplier"之后
- Preferences 方法：放在 `getFakeUploadRatio/setFakeUploadRatio` 之后

### 4. 默认值处理
- CheckBox 默认为选中状态（true）
- 配置文件默认值为 true
- 使用 `setChecked()` 方法设置初始状态

### 5. 国际化支持
所有用户可见文本都使用 `tr()` 函数包裹：
```cpp
tr("Fake upload ratio randomization")
```

---

## 测试建议

### 1. 功能测试
- [ ] 打开 Advanced Settings 对话框，确认新设置项显示正确
- [ ] 确认 CheckBox 默认为选中状态
- [ ] 取消选中，点击"应用"按钮
- [ ] 重启 qBittorrent，确认设置被正确保存和加载
- [ ] 检查配置文件中是否正确写入 `FakeUploadRatioRandomization` 值

### 2. 界面测试
- [ ] 确认 CheckBox 位置在 qBittorrent Section 中
- [ ] 确认显示在"Fake upload ratio multiplier"之后
- [ ] 确认默认为选中状态

### 3. 配置持久化测试
```bash
# 查看配置文件
cat ~/.config/qBittorrent/qBittorrent.ini | grep FakeUploadRatio

# 预期输出：
# Advanced\FakeUploadRatio=1
# Advanced\FakeUploadRatioRandomization=true
```

### 4. 功能逻辑测试
- [ ] 设置 Multiplier 为 2x，启用 Randomization
- [ ] 观察实际上传量是否有波动
- [ ] 禁用 Randomization，观察上传量是否固定为 2x

---

## 与第一个功能的关系

这是对"Fake upload ratio multiplier"功能的补充：

### 第一个功能（Fake Upload Ratio Multiplier）
- **类型**: ComboBox
- **选项**: 1x ~ 5x
- **默认**: 1x (Disabled)
- **作用**: 设置上传量的固定倍数

### 第二个功能（Fake Upload Ratio Randomization）
- **类型**: CheckBox
- **状态**: 启用/禁用
- **默认**: 启用（true）
- **作用**: 在固定倍数基础上添加随机波动

### 配合使用示例

```
场景 1: 保守使用
- Multiplier: 1x (Disabled)
- Randomization: ☑ Enabled
- 效果: 接近真实上传量，略有波动

场景 2: 中等伪造
- Multiplier: 2x
- Randomization: ☑ Enabled
- 效果: 约 2 倍上传，带随机波动（1.8x ~ 2.2x）

场景 3: 固定倍数
- Multiplier: 3x
- Randomization: ☐ Disabled
- 效果: 严格 3 倍上传，无波动

场景 4: 激进伪造
- Multiplier: 5x
- Randomization: ☑ Enabled
- 效果: 约 5 倍上传，带随机波动（4.5x ~ 5.5x）
```

---

## 后续工作

### 1. 实现随机化逻辑

在 `src/base/bittorrent/sessionimpl.cpp` 中实现随机化算法：

```cpp
qint64 SessionImpl::getAdjustedUploadAmount(qint64 actualUpload) const
{
    const Preferences *pref = Preferences::instance();
    const int ratio = pref->getFakeUploadRatio();
    
    // 应用基础倍数
    qint64 adjustedUpload = actualUpload * ratio;
    
    // 如果启用随机化
    if (pref->isFakeUploadRatioRandomizationEnabled())
    {
        // 生成 0.9 ~ 1.1 范围内的随机因子（±10% 波动）
        const double randomFactor = 0.9 + (QRandomGenerator::global()->bounded(20) / 100.0);
        adjustedUpload = static_cast<qint64>(adjustedUpload * randomFactor);
    }
    
    return adjustedUpload;
}
```

### 2. 随机化参数可配置

未来可以考虑添加随机化范围的配置：
- 当前：固定 ±10% 波动
- 改进：允许用户配置波动范围（例如 ±5% ~ ±20%）

### 3. 添加工具提示

建议添加详细的工具提示说明：

```cpp
m_checkBoxFakeUploadRatioRandomization.setToolTip(
    tr("Add random fluctuation to the upload ratio multiplier to make it look more natural. "
       "Recommended to keep enabled to avoid detection.")
);
```

### 4. 添加警告

在文档中说明：
- 即使启用随机化，仍可能被某些 Tracker 检测
- 随机化不能完全消除被封禁的风险

---

## 注意事项

⚠️ **重要提醒**：

1. **默认开启**: 该功能默认为开启状态，更符合实际使用场景
2. **配合使用**: 建议与 Multiplier 功能配合使用，单独使用意义不大
3. **检测风险**: 即使添加随机化，仍可能被 Tracker 检测异常模式
4. **合理波动**: 随机波动范围不宜过大，建议控制在 ±10% 以内
5. **性能影响**: 随机数生成对性能影响极小，可以忽略不计

---

## 版本信息

- **添加日期**: 2025-12-13
- **qBittorrent 版本**: 5.x
- **修改文件数**: 4 个
- **新增代码行数**: 约 20 行
- **依赖功能**: Fake upload ratio multiplier

---

## 参考资源

- [Fake Upload Ratio Multiplier 功能文档](./FakeUploadRatio_Feature.md)
- [qBittorrent Advanced Settings 架构文档](./AdvancedSettings_Architecture.md)
- [qBittorrent 代码规范](https://github.com/qbittorrent/qBittorrent/wiki/Coding-Guidelines)
- [Qt CheckBox 文档](https://doc.qt.io/qt-6/qcheckbox.html)
- [Qt QRandomGenerator 文档](https://doc.qt.io/qt-6/qrandomgenerator.html)
