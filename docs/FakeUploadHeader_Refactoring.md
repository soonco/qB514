# Fake Upload Header Refactoring

## 概述

将 `FAKE_UPLOAD_RATIO` 和 `FAKE_UPLOAD_RATIO_RANDOMIZATION` 两个设置项从 qBittorrent Section 中独立出来，创建一个新的 **Fake Upload Section**，仿照 QBITTORRENT_HEADER 和 LIBTORRENT_HEADER 的设计模式。

## 修改内容

### 1. 枚举结构调整

**文件**: `/src/gui/advancedsettings.cpp`

#### 修改前的结构

```cpp
enum AdvSettingsRows
{
    QBITTORRENT_HEADER,
    // ... qBittorrent 设置项
    RECHECK_COMPLETED,
    FAKE_UPLOAD_RATIO,              // 在 qBittorrent Section 中
    FAKE_UPLOAD_RATIO_RANDOMIZATION, // 在 qBittorrent Section 中
    APP_INSTANCE_NAME,
    // ... 更多 qBittorrent 设置项
    SESSION_SHUTDOWN_TIMEOUT,
    
    LIBTORRENT_HEADER,
    // ... libtorrent 设置项
};
```

#### 修改后的结构

```cpp
enum AdvSettingsRows
{
    QBITTORRENT_HEADER,
    // ... qBittorrent 设置项
    RECHECK_COMPLETED,
    APP_INSTANCE_NAME,              // FAKE_UPLOAD 相关项已移除
    // ... 更多 qBittorrent 设置项
    SESSION_SHUTDOWN_TIMEOUT,
    
    // 伪造上传部分
    // Fake upload section
    FAKE_UPLOAD_HEADER,             // ← 新增分组标题
    FAKE_UPLOAD_RATIO,              // ← 移动到新分组
    FAKE_UPLOAD_RATIO_RANDOMIZATION,// ← 移动到新分组
    
    LIBTORRENT_HEADER,
    // ... libtorrent 设置项
};
```

**位置**: 在 `SESSION_SHUTDOWN_TIMEOUT` 之后，`LIBTORRENT_HEADER` 之前

---

### 2. 添加分组标题

**文件**: `/src/gui/advancedsettings.cpp:591-599`

```cpp
auto *labelFakeUploadLink = new QLabel(
    makeLink(u"https://github.com/qbittorrent/qBittorrent/wiki/Explanation-of-Options-in-qBittorrent#Advanced"
             , tr("Open documentation"))
    , this);
labelFakeUploadLink->setOpenExternalLinks(true);
addRow(FAKE_UPLOAD_HEADER, u"<b>%1</b>"_s.arg(tr("Fake Upload Section")), labelFakeUploadLink);
static_cast<QLabel *>(cellWidget(FAKE_UPLOAD_HEADER, PROPERTY))->setAlignment(Qt::AlignCenter | Qt::AlignVCenter);
```

**特点**:
- 粗体居中显示
- 包含"Open documentation"链接
- 链接指向 qBittorrent Wiki
- 与 QBITTORRENT_HEADER 和 LIBTORRENT_HEADER 风格一致

---

### 3. 调整设置项位置

**文件**: `/src/gui/advancedsettings.cpp`

#### 从原位置移除（第 918-930 行）

移除了以下代码：
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
```

#### 添加到新位置（第 1087-1101 行）

在 `SESSION_SHUTDOWN_TIMEOUT` 之后添加：
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
```

---

## 界面效果

### 修改前

```
┌────────────────────────────────────────────────────────────────────┐
│          **qBittorrent Section**           │ Open documentation    │
├────────────────────────────────────────────────────────────────────┤
│ ...                                        │ ...                   │
│ Recheck torrents on completion             │ [☐]                  │
│ Fake upload ratio multiplier               │ [1x (Disabled) ▼]    │
│ Fake upload ratio randomization            │ [☑]                  │
│ Customize application instance name        │ [____________]       │
│ ...                                        │ ...                   │
│ BitTorrent session shutdown timeout        │ [60      ] sec       │
├────────────────────────────────────────────────────────────────────┤
│          **libtorrent Section**            │ Open documentation    │
├────────────────────────────────────────────────────────────────────┤
│ Bdecode depth limit                        │ [100     ]           │
│ ...                                        │ ...                   │
└────────────────────────────────────────────────────────────────────┘
```

### 修改后

```
┌────────────────────────────────────────────────────────────────────┐
│          **qBittorrent Section**           │ Open documentation    │
├────────────────────────────────────────────────────────────────────┤
│ ...                                        │ ...                   │
│ Recheck torrents on completion             │ [☐]                  │
│ Customize application instance name        │ [____________]       │
│ ...                                        │ ...                   │
│ BitTorrent session shutdown timeout        │ [60      ] sec       │
├────────────────────────────────────────────────────────────────────┤
│          **Fake Upload Section**           │ Open documentation    │  ← 新增分组
├────────────────────────────────────────────────────────────────────┤
│ Fake upload ratio multiplier               │ [1x (Disabled) ▼]    │  ← 移动到此
│ Fake upload ratio randomization            │ [☑]                  │  ← 移动到此
├────────────────────────────────────────────────────────────────────┤
│          **libtorrent Section**            │ Open documentation    │
├────────────────────────────────────────────────────────────────────┤
│ Bdecode depth limit                        │ [100     ]           │
│ ...                                        │ ...                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 设计模式

### 三大分组结构

修改后，Advanced Settings 界面现在有三个主要分组：

| 分组 | 枚举常量 | 标题文本 | 文档链接 |
|------|---------|---------|---------|
| **qBittorrent Section** | `QBITTORRENT_HEADER` | qBittorrent Section | qBittorrent Wiki |
| **Fake Upload Section** | `FAKE_UPLOAD_HEADER` | Fake Upload Section | qBittorrent Wiki |
| **libtorrent Section** | `LIBTORRENT_HEADER` | libtorrent Section | libtorrent Docs |

### 分组标题的共同特征

1. **粗体居中**: 使用 `<b>` 标签和 `Qt::AlignCenter`
2. **文档链接**: 右侧显示"Open documentation"链接
3. **外部打开**: 链接在浏览器中打开
4. **一致风格**: 所有分组标题使用相同的样式

---

## 优势

### 1. 更好的组织结构

- **逻辑分组**: Fake Upload 相关功能独立成组，更清晰
- **易于扩展**: 未来可以在 Fake Upload Section 中添加更多相关功能
- **减少混乱**: qBittorrent Section 不再包含过多设置项

### 2. 一致的设计模式

- **遵循现有模式**: 与 QBITTORRENT_HEADER 和 LIBTORRENT_HEADER 保持一致
- **标准化**: 所有分组使用相同的标题样式和文档链接
- **可维护性**: 代码结构清晰，易于理解和修改

### 3. 用户体验改善

- **更易查找**: 用户可以快速定位到 Fake Upload 相关设置
- **视觉分隔**: 明确的分组标题提供更好的视觉层次
- **专业性**: 独立的分组体现了功能的重要性

---

## 代码风格

### 1. 枚举位置

```cpp
// 伪造上传部分
// Fake upload section
FAKE_UPLOAD_HEADER,
FAKE_UPLOAD_RATIO,
FAKE_UPLOAD_RATIO_RANDOMIZATION,
```

- 中英文双语注释
- 分组标题在前，设置项在后
- 与其他分组保持一致的缩进和格式

### 2. 标题行代码

```cpp
auto *labelFakeUploadLink = new QLabel(
    makeLink(u"https://github.com/qbittorrent/qBittorrent/wiki/..."
             , tr("Open documentation"))
    , this);
labelFakeUploadLink->setOpenExternalLinks(true);
addRow(FAKE_UPLOAD_HEADER, u"<b>%1</b>"_s.arg(tr("Fake Upload Section")), labelFakeUploadLink);
static_cast<QLabel *>(cellWidget(FAKE_UPLOAD_HEADER, PROPERTY))->setAlignment(Qt::AlignCenter | Qt::AlignVCenter);
```

- 使用 `makeLink` 辅助函数创建链接
- 使用 `tr()` 支持国际化
- 使用 `u"..."_s` 字符串字面量
- 设置居中对齐

### 3. 设置项顺序

在 `loadAdvancedSettings()` 中：
1. 先添加所有分组标题（QBITTORRENT_HEADER, LIBTORRENT_HEADER, FAKE_UPLOAD_HEADER）
2. 再按照枚举顺序添加各个设置项
3. 保持与枚举定义的一致性

---

## 配置文件

配置文件格式**不受影响**，仍然保存在 `[Preferences]` 分组下：

```ini
[Preferences]
Advanced\FakeUploadRatio=2
Advanced\FakeUploadRatioRandomization=true
```

---

## 测试建议

### 1. 界面测试

- [ ] 打开 Advanced Settings 对话框
- [ ] 确认出现三个分组标题：qBittorrent Section、Fake Upload Section、libtorrent Section
- [ ] 确认 Fake Upload Section 位于 qBittorrent 和 libtorrent 之间
- [ ] 确认标题为粗体居中显示
- [ ] 确认"Open documentation"链接可以点击

### 2. 功能测试

- [ ] 修改 Fake upload ratio multiplier，确认可以保存
- [ ] 修改 Fake upload ratio randomization，确认可以保存
- [ ] 重启 qBittorrent，确认设置被正确加载
- [ ] 确认配置文件中的值正确

### 3. 视觉测试

- [ ] 确认分组标题与其他两个分组风格一致
- [ ] 确认设置项在正确的分组下
- [ ] 确认没有布局错乱或重叠

---

## 未来扩展

在 Fake Upload Section 中可以添加更多相关功能：

### 可能的新功能

1. **Fake download ratio multiplier** - 伪造下载倍数
2. **Fake ratio schedule** - 按时间段设置不同倍数
3. **Per-tracker fake ratio** - 针对不同 Tracker 设置不同倍数
4. **Fake ratio whitelist** - 白名单 Tracker（不伪造）
5. **Randomization range** - 自定义随机波动范围

### 添加新功能的步骤

1. 在 `FAKE_UPLOAD_RATIO_RANDOMIZATION` 之后添加枚举项
2. 在头文件中声明控件
3. 在 `loadAdvancedSettings()` 中初始化控件（在 FAKE_UPLOAD_RATIO_RANDOMIZATION 之后）
4. 在 `saveAdvancedSettings()` 中保存设置
5. 在 Preferences 类中添加 getter/setter 方法

---

## 相关文件

- `/src/gui/advancedsettings.cpp` - 主要修改文件
- `/src/gui/advancedsettings.h` - 无需修改（控件声明已存在）
- `/src/base/preferences.h` - 无需修改（方法声明已存在）
- `/src/base/preferences.cpp` - 无需修改（方法实现已存在）

---

## 版本历史

- **v1.0** (2025-12-13): 初始版本，创建 FAKE_UPLOAD_HEADER 分组

---

## 参考资源

- [Fake Upload Ratio Multiplier 功能文档](./FakeUploadRatio_Feature.md)
- [Fake Upload Ratio Randomization 功能文档](./FakeUploadRatioRandomization_Feature.md)
- [qBittorrent Advanced Settings 架构文档](./AdvancedSettings_Architecture.md)
- [qBittorrent 代码规范](https://github.com/qbittorrent/qBittorrent/wiki/Coding-Guidelines)

---

**文档版本**: 1.0  
**最后更新**: 2025-12-13  
**适用版本**: qBittorrent 5.x
