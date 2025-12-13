# Fake Upload Ratio Multiplier Feature

## 功能概述

在 qBittorrent Advanced Settings 的 qBittorrent Section 中新增了"Fake upload ratio multiplier"（伪造上传倍数）功能，允许用户选择 1-5 倍的上传倍数，默认为 1 倍（禁用状态）。

## 修改文件清单

### 1. `/src/gui/advancedsettings.cpp`

#### 修改 1: 在枚举中添加行标识（第 92 行）

```cpp
enum AdvSettingsRows
{
    // ...
    RECHECK_COMPLETED,  // 完成后重新检查 Recheck completed
    FAKE_UPLOAD_RATIO,  // 伪造上传倍数 Fake upload ratio multiplier  // ← 新增
    // UI 相关
    // UI related
    APP_INSTANCE_NAME,  // 应用实例名称 App instance name
    // ...
};
```

**位置**: 在 `RECHECK_COMPLETED` 之后，`APP_INSTANCE_NAME` 之前
**作用**: 定义该设置项在表格中的行号

#### 修改 2: 在 loadAdvancedSettings 中初始化控件（第 899-907 行）

```cpp
// 完成时重新检查种子
// Recheck completed torrents
m_checkBoxRecheckCompleted.setChecked(pref->recheckTorrentsOnCompletion());
addRow(RECHECK_COMPLETED, tr("Recheck torrents on completion"), &m_checkBoxRecheckCompleted);

// 伪造上传倍数
// Fake upload ratio multiplier
m_comboBoxFakeUploadRatio.addItem(tr("1x (Disabled)"), 1);
m_comboBoxFakeUploadRatio.addItem(tr("2x"), 2);
m_comboBoxFakeUploadRatio.addItem(tr("3x"), 3);
m_comboBoxFakeUploadRatio.addItem(tr("4x"), 4);
m_comboBoxFakeUploadRatio.addItem(tr("5x"), 5);
m_comboBoxFakeUploadRatio.setCurrentIndex(m_comboBoxFakeUploadRatio.findData(pref->getFakeUploadRatio()));
addRow(FAKE_UPLOAD_RATIO, tr("Fake upload ratio multiplier"), &m_comboBoxFakeUploadRatio);

// 自定义应用程序实例名称
// Customize application instance name
```

**功能说明**:
- 添加 5 个选项：1x (Disabled)、2x、3x、4x、5x
- 每个选项的数据值为对应的倍数（1-5）
- 从配置中读取当前值并设置为选中项
- 将控件添加到界面的 FAKE_UPLOAD_RATIO 行

#### 修改 3: 在 saveAdvancedSettings 中保存设置（第 345-347 行）

```cpp
// 完成后重新检查种子
// Recheck torrents on completion
pref->recheckTorrentsOnCompletion(m_checkBoxRecheckCompleted.isChecked());

// 伪造上传倍数
// Fake upload ratio multiplier
pref->setFakeUploadRatio(m_comboBoxFakeUploadRatio.currentData().toInt());

// 自定义应用实例名称
// Customize application instance name
app()->setInstanceName(m_lineEditAppInstanceName.text());
```

**功能说明**:
- 获取 ComboBox 当前选中项的数据值（1-5）
- 调用 Preferences 的 setter 方法保存到配置

---

### 2. `/src/gui/advancedsettings.h`

#### 修改: 声明 ComboBox 控件成员（第 85 行）

```cpp
QComboBox m_comboBoxInterface, m_comboBoxInterfaceAddress, m_comboBoxDiskIOReadMode, 
          m_comboBoxDiskIOWriteMode, m_comboBoxUtpMixedMode, m_comboBoxChokingAlgorithm,
          m_comboBoxSeedChokingAlgorithm, m_comboBoxResumeDataStorage, 
          m_comboBoxTorrentContentRemoveOption, m_comboBoxFakeUploadRatio;  // ← 新增
```

**作用**: 声明用于显示伪造上传倍数选项的 ComboBox 控件

---

### 3. `/src/base/preferences.h`

#### 修改: 添加 getter/setter 方法声明（第 292-293 行）

```cpp
bool recheckTorrentsOnCompletion() const;
void recheckTorrentsOnCompletion(bool recheck);
int getFakeUploadRatio() const;           // ← 新增
void setFakeUploadRatio(int ratio);       // ← 新增
bool resolvePeerCountries() const;
void resolvePeerCountries(bool resolve);
```

**作用**: 声明配置读取和保存方法

---

### 4. `/src/base/preferences.cpp`

#### 修改: 实现 getter/setter 方法（第 1307-1319 行）

```cpp
bool Preferences::recheckTorrentsOnCompletion() const
{
    return value(u"Preferences/Advanced/RecheckOnCompletion"_s, false);
}

void Preferences::recheckTorrentsOnCompletion(const bool recheck)
{
    if (recheck == recheckTorrentsOnCompletion())
        return;

    setValue(u"Preferences/Advanced/RecheckOnCompletion"_s, recheck);
}

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

bool Preferences::resolvePeerCountries() const
{
    return value(u"Preferences/Advanced/ResolveCountries"_s, true);
}
```

**功能说明**:
- `getFakeUploadRatio()`: 从配置读取伪造上传倍数，默认值为 1
- `setFakeUploadRatio()`: 保存伪造上传倍数到配置
- 配置键名: `Preferences/Advanced/FakeUploadRatio`
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
Advanced\FakeUploadRatio=1
```

### 可选值

| 值 | 显示文本 | 说明 |
|----|---------|------|
| 1  | 1x (Disabled) | 默认值，不进行倍数伪造 |
| 2  | 2x | 2 倍上传 |
| 3  | 3x | 3 倍上传 |
| 4  | 4x | 4 倍上传 |
| 5  | 5x | 5 倍上传 |

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
│ Fake upload ratio multiplier               │ [1x (Disabled) ▼]    │  ← 新增
│ Customize application instance name        │ [____________]       │
│ Refresh interval                           │ [1500    ] ms        │
│ ...                                        │ ...                   │
└────────────────────────────────────────────────────────────────────┘
```

点击下拉框可选择：
- 1x (Disabled)
- 2x
- 3x
- 4x
- 5x

---

## 代码风格说明

本次修改严格遵循 qBittorrent 的代码风格：

### 1. 命名规范
- **枚举常量**: 大写下划线分隔（`FAKE_UPLOAD_RATIO`）
- **成员变量**: 小驼峰 + m_ 前缀（`m_comboBoxFakeUploadRatio`）
- **方法名**: 小驼峰（`getFakeUploadRatio`、`setFakeUploadRatio`）
- **配置键**: 路径式命名（`Preferences/Advanced/FakeUploadRatio`）

### 2. 注释风格
```cpp
// 中文注释
// English comment
```
每个功能块都有中英文双语注释

### 3. 位置选择
- 枚举：放在 `RECHECK_COMPLETED` 之后，属于 behavior 设置组
- 界面：显示在"Recheck torrents on completion"和"Customize application instance name"之间
- Preferences 方法：放在 `recheckTorrentsOnCompletion` 之后

### 4. 默认值处理
- ComboBox 默认选中 1x (Disabled)
- 配置文件默认值为 1
- 使用 `findData()` 方法根据数值查找索引

### 5. 国际化支持
所有用户可见文本都使用 `tr()` 函数包裹：
```cpp
tr("Fake upload ratio multiplier")
tr("1x (Disabled)")
tr("2x")
```

---

## 测试建议

### 1. 功能测试
- [ ] 打开 Advanced Settings 对话框，确认新设置项显示正确
- [ ] 选择不同倍数（1x-5x），点击"应用"按钮
- [ ] 重启 qBittorrent，确认设置被正确保存和加载
- [ ] 检查配置文件中是否正确写入 `FakeUploadRatio` 值

### 2. 界面测试
- [ ] 确认 ComboBox 位置在 qBittorrent Section 中
- [ ] 确认显示在"Recheck torrents on completion"之后
- [ ] 确认下拉框包含 5 个选项
- [ ] 确认默认选中 1x (Disabled)

### 3. 配置持久化测试
```bash
# 查看配置文件
cat ~/.config/qBittorrent/qBittorrent.ini | grep FakeUploadRatio

# 预期输出：
# Advanced\FakeUploadRatio=1
```

### 4. 国际化测试
- [ ] 切换不同语言，确认文本正确翻译（需要添加翻译文件）

---

## 后续工作

### 1. 实现实际功能逻辑
当前代码只完成了 UI 和配置持久化，实际的上传倍数伪造逻辑需要在以下位置实现：

- **BitTorrent::Session**: 在上传统计时应用倍数
- **TorrentHandle**: 修改上传量报告
- **Tracker 通告**: 修改向 Tracker 报告的上传量

建议在 `src/base/bittorrent/sessionimpl.cpp` 中实现：

```cpp
// 示例伪代码
qint64 SessionImpl::getAdjustedUploadAmount(qint64 actualUpload) const
{
    const int ratio = Preferences::instance()->getFakeUploadRatio();
    return actualUpload * ratio;
}
```

### 2. 添加翻译
在翻译文件中添加以下条目：
- `Fake upload ratio multiplier`
- `1x (Disabled)`
- `2x` / `3x` / `4x` / `5x`

### 3. 更新文档
- 更新用户手册，说明该功能的用途和风险
- 添加警告：使用该功能可能违反某些 Tracker 的规则

### 4. 添加警告提示
建议在设置项旁添加工具提示：

```cpp
m_comboBoxFakeUploadRatio.setToolTip(
    tr("WARNING: Using fake upload ratio may violate tracker rules and result in account ban")
);
```

---

## 注意事项

⚠️ **重要提醒**：

1. **合规性**: 伪造上传量可能违反某些 Private Tracker 的规则，使用前请确认是否允许
2. **检测风险**: 某些 Tracker 可能检测异常的上传/下载比例
3. **道德考量**: 该功能可能影响 BitTorrent 网络的公平性
4. **仅用于测试**: 建议仅在测试环境或允许的场景下使用

---

## 版本信息

- **添加日期**: 2025-12-13
- **qBittorrent 版本**: 5.x
- **修改文件数**: 4 个
- **新增代码行数**: 约 30 行

---

## 参考资源

- [qBittorrent Advanced Settings 架构文档](./AdvancedSettings_Architecture.md)
- [qBittorrent 代码规范](https://github.com/qbittorrent/qBittorrent/wiki/Coding-Guidelines)
- [Qt ComboBox 文档](https://doc.qt.io/qt-6/qcombobox.html)
